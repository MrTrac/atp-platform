"""aios-identity access token for the ATP -> aios-flow call (aios-flow >= 1.2.0 enforces `Authorization: Bearer <access token>`).

ATP is a machine caller: it signs in as the service account `svc:atp` (role `service-account`), which aios-flow lets start and read runs and never lets resolve an
approval. This module owns everything about that token and nothing else: where the credentials come from, how a token is obtained, how long it is kept.
`aios_flow_adapter` attaches it to aios-flow requests and to nothing else (see `tests/unit/test_aios_flow_auth.py`, which fails if another module imports this one).

Configuration (environment; nothing is read from the repo and nothing is written anywhere):

    AIOS_FLOW_IDENTITY_URL      identity base URL, e.g. https://103.245.255.211.sslip.io/identity. https, or a loopback address. UNSET = authentication is not
                                configured: no token is requested or sent, and the adapter behaves exactly as before 2.7 (right for an aios-flow that does not enforce).
    AIOS_FLOW_IDENTITY_SECRET   the secret of the service account (>= 16 characters, identity's rule). Set but empty while the URL is set = an error at the first
                                call, never a silent downgrade to unauthenticated. On macOS it comes from the login Keychain through scripts/bridge_with_keychain.sh
                                (service name == variable name); on aios-server from a root-owned EnvironmentFile.
    AIOS_FLOW_IDENTITY_USER     optional, default `svc:atp`.

Exchange: POST {identity}/service-account/token {"username", "secret", "consumer": "ATP"} -> {"access_token", "expires_in", "token_type", "session_id"}.

Lifetime. Measured 14/10/2026 against aios-identity 1.2.4: the answer advertises `expires_in` = 31536000 (1 year) but the JWT really lives 3600 s (`exp - iat`),
and the server enforces the JWT. So `expires_in` is ignored: the lifetime is `exp - iat` read from the token itself (no signature check — this is our own token, the
server verifies it; `iat` rather than the local clock so that a skewed clock cannot shorten or lengthen it), 3600 s when the token cannot be read. The token is
renewed `min(300 s, lifetime / 2)` before it ends (55 minutes for today's 3600 s) and survives a later identity fix that makes the lifetime longer.

Every mint creates a session row at identity that lives for a year, so minting is rationed: one token is shared by all threads (one mint at a time, the others wait for
its result), a token that aios-flow rejected is replaced at most once per 30 s, a refusal of the credentials themselves (wrong secret, wrong URL) is remembered for 60 s
and an identity that cannot be reached for 1 s, instead of every queued caller waiting out its own timeout. When the renewal fails but the cached token has not yet
expired it is served again (stale-while-error). Time is the wall clock: `time.monotonic` stops while a Mac sleeps, and the JWT's `exp` does not.

The secret and the token are never logged, never put in an error text (identity's own message is scrubbed of the secret before it is used), never in `repr()`, and
the G9 trace record of the mint carries only the route and the outcome.
"""

from __future__ import annotations

import base64
import ipaddress
import json
import os
import re
import ssl
import threading
import time
from typing import Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, getproxies, proxy_bypass, urlopen

from core.http_errors import close_http_error, error_code_and_message, network_reason, read_error_body
from core.trace import generate_request_id, record_trace, trace_headers

ENV_URL = "AIOS_FLOW_IDENTITY_URL"
ENV_SECRET = "AIOS_FLOW_IDENTITY_SECRET"
ENV_USER = "AIOS_FLOW_IDENTITY_USER"
DEFAULT_USERNAME = "svc:atp"
CONSUMER = "ATP"

_CONTRACT = "ATP_aios-identity_v1"
_MINT_TIMEOUT_S = 10.0
_ASSUMED_LIFETIME_S = 3600.0  # what identity 1.2.4 really issues, used only when the token's own exp/iat cannot be read
_REFRESH_MARGIN_S = 300.0
_REMINT_COOLDOWN_S = 30.0
_DENIAL_TTL_S = 60.0
_UNAVAILABLE_TTL_S = 1.0  # how long "identity cannot be reached" is remembered, so queued callers fail at once instead of each waiting out a timeout; must stay below core.retry's 1 s base delay or a retry would only meet the memory
_EXPIRY_SAFETY_S = 15.0
_TOKEN_SHAPE = re.compile(r"[A-Za-z0-9\-._~+/]+=*")  # the RFC 6750 alphabet aios-flow accepts; also keeps a CR/LF out of a header


class AuthError(Exception):
    """Authentication cannot succeed as things stand: aios-flow refused the token (401/403), aios-identity refused the credentials, or the configuration is
    unusable. Retrying does not help; an operator has to act. `source` is "aios-flow", "aios-identity" or "config"; `code` is the server's error code when it sent one."""

    def __init__(self, message: str, *, code: str, source: str, http_status: int | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.source = source
        self.http_status = http_status


class IdentityUnavailable(URLError):
    """aios-identity could not issue a token right now (unreachable, 429, 5xx). Transient. A URLError so that `core.retry.with_retry` treats it like any other network error."""

    def __init__(self, message: str, *, http_status: int | None = None) -> None:
        super().__init__(message)
        self.http_status = http_status

    def __str__(self) -> str:
        return str(self.reason)


def _is_loopback(host: str | None) -> bool:
    if not host:
        return False
    host = host.lower()
    if host == "localhost" or host.endswith(".localhost"):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _proxy_in_the_way(scheme: str, host: str) -> bool:
    """urllib sends an http:// request through the proxy of HTTP_PROXY / the macOS system settings unless NO_PROXY (or the exceptions list) names the host."""
    return bool(getproxies().get(scheme)) and not proxy_bypass(host)


def check_transport(url: str, *, what: str) -> None:
    """A secret or a token may only travel over https, or to this machine. Raises AuthError otherwise. Only scheme://host is ever put in the message
    (a URL may carry credentials in its userinfo).

    "To this machine" must stay true: with an http proxy configured for the host, an http://localhost request would be handed to the proxy, in clear text."""
    try:
        parts = urlsplit(url)
        host = parts.hostname
    except ValueError:  # e.g. an unterminated IPv6 literal
        parts, host = None, None
    if host and parts.scheme == "https":
        return
    if host and parts.scheme == "http" and _is_loopback(host):
        if not _proxy_in_the_way("http", host):
            return
        raise AuthError(
            f"{what} is http://{host}, but an http proxy is configured and would receive the secret or token in clear text: add {host} to NO_PROXY",
            code="proxy_in_the_way",
            source="config",
        )
    shown = f"{parts.scheme}://{host}" if parts is not None and parts.scheme and host else "an unparseable URL"
    raise AuthError(
        f"{what} is {shown}: an identity secret or token is only sent over https, or to a loopback address",
        code="insecure_transport",
        source="config",
    )


def _scrub(text: str, secret: str) -> str:
    return text.replace(secret, "***") if len(secret) >= 4 else text


def _jwt_lifetime_s(token: str) -> float | None:
    """`exp - iat` of a JWT, or None when it cannot be read. The signature is not checked: this only schedules our own renewal."""
    try:
        segment = token.split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(segment + "=" * (-len(segment) % 4)))
        exp, iat = claims["exp"], claims["iat"]
        if isinstance(exp, (int, float)) and isinstance(iat, (int, float)) and exp > iat:
            return float(exp - iat)
    except (IndexError, KeyError, TypeError, AttributeError, ValueError):
        pass
    return None


class IdentityTokenProvider:
    """Obtains and caches the access token of one service account. Thread-safe."""

    def __init__(
        self,
        identity_url: str,
        secret: str,
        *,
        username: str = DEFAULT_USERNAME,
        consumer: str = CONSUMER,
        timeout_s: float = _MINT_TIMEOUT_S,
        clock: Callable[[], float] | None = None,
    ) -> None:
        check_transport(identity_url, what=ENV_URL)
        self._base = identity_url.rstrip("/")
        self._secret = secret
        self.username = username
        self._consumer = consumer
        self._timeout_s = timeout_s
        self._clock = clock if clock is not None else time.time  # wall clock: monotonic time stops while a laptop sleeps
        self._lock = threading.Lock()
        self._token: str | None = None
        self._minted_at: float | None = None
        self._refresh_at = 0.0
        self._expires_at = 0.0
        self._unavailable: tuple[str, int | None] | None = None
        self._unavailable_until = 0.0
        self._denial: tuple[str, str, str, int | None] | None = None
        self._denied_until = 0.0

    def __repr__(self) -> str:
        parts = urlsplit(self._base)
        return f"IdentityTokenProvider(identity={parts.scheme}://{parts.hostname}, username={self.username!r})"

    def matches(self, identity_url: str, secret: str, username: str) -> bool:
        return self._base == identity_url.rstrip("/") and self._secret == secret and self.username == username

    # -- public ----------------------------------------------------------------------------------------------------------------------------------------

    def get_token(self) -> str:
        """The cached token while it is fresh, else a new one. Raises AuthError (credentials refused, unusable configuration) or IdentityUnavailable (transient)."""
        with self._lock:
            now = self._clock()
            if self._token is not None and now < self._refresh_at:
                return self._token
            try:
                return self._mint_locked()
            except IdentityUnavailable:
                if self._token is not None and now < self._expires_at:
                    return self._token  # the renewal failed but the token still has time: keep using it
                raise

    def refresh_after_rejection(self, rejected: str) -> str | None:
        """aios-flow answered 401 to `rejected`. Returns a different token to retry with, or None when asking identity again cannot help right now.

        If another thread has already replaced `rejected` that token is returned without a mint. If `rejected` is itself younger than 30 s, aios-flow turned down
        something identity has just issued, so a second mint would be refused the same way and only add a session row: None. Raises as `get_token` does."""
        with self._lock:
            if self._token is not None and self._token != rejected:
                return self._token
            if self._minted_at is not None and self._clock() - self._minted_at < _REMINT_COOLDOWN_S:
                return None
            self._token = None
            return self._mint_locked()

    # -- internals (the lock is held) --------------------------------------------------------------------------------------------------------------------

    def _mint_locked(self) -> str:
        now = self._clock()
        if self._denial is not None:
            if now < self._denied_until:
                message, code, source, status = self._denial
                raise AuthError(message, code=code, source=source, http_status=status)
            self._denial = None
        if self._unavailable is not None:
            if now < self._unavailable_until:
                message, status = self._unavailable
                raise IdentityUnavailable(message, http_status=status)
            self._unavailable = None
        req_id = generate_request_id()
        request = Request(
            f"{self._base}/service-account/token",
            data=json.dumps({"username": self.username, "secret": self._secret, "consumer": self._consumer}).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json", **trace_headers(req_id)},
            method="POST",
        )
        t0 = time.monotonic()
        outcome = "error"
        try:
            token = self._exchange(request)
            outcome = "ok"
        except AuthError as err:
            self._denial = (str(err), err.code, err.source, err.http_status)
            self._denied_until = now + _DENIAL_TTL_S
            raise
        except IdentityUnavailable as err:
            self._unavailable = (str(err), err.http_status)
            self._unavailable_until = self._clock() + _UNAVAILABLE_TTL_S  # measured after the attempt: callers queued behind it fail at once
            raise
        finally:
            record_trace(
                request_id=req_id,
                target_module="aios-identity",
                route="/service-account/token",
                method="POST",
                status=outcome,
                duration_ms=int((time.monotonic() - t0) * 1000),
                contract_version=_CONTRACT,
            )
        lifetime = _jwt_lifetime_s(token) or _ASSUMED_LIFETIME_S
        self._token = token
        self._minted_at = now  # taken before the call: a slow mint only makes the renewal earlier
        self._refresh_at = now + lifetime - min(_REFRESH_MARGIN_S, lifetime / 2)
        self._expires_at = now + lifetime - min(_EXPIRY_SAFETY_S, lifetime / 2)
        return token

    def _exchange(self, request: Request) -> str:
        try:
            with urlopen(request, timeout=self._timeout_s) as resp:
                answer = json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            status = exc.code
            code, message = error_code_and_message(read_error_body(exc))
            close_http_error(exc)
            raise self._refusal(status, code, message) from None
        except (URLError, OSError) as exc:  # an HTTPError never gets here: the handler above takes it
            reason = network_reason(exc)
            if isinstance(reason, ssl.SSLCertVerificationError):
                raise AuthError(
                    f"aios-identity's TLS certificate was not accepted: {_scrub(str(reason), self._secret)}",
                    code="tls_verification_failed",
                    source="config",
                ) from None
            raise IdentityUnavailable(f"aios-identity unreachable: {_scrub(str(reason), self._secret)}") from None
        except ValueError:
            raise IdentityUnavailable("aios-identity answered with something that is not JSON") from None
        token = answer.get("access_token") if isinstance(answer, dict) else None
        if not isinstance(token, str) or not _TOKEN_SHAPE.fullmatch(token):
            raise AuthError(
                "aios-identity answered 200 without a usable access_token",
                code="bad_response",
                source="aios-identity",
            )
        return token

    def _refusal(self, status: int, code: str | None, message: str | None) -> Exception:
        detail = f"HTTP {status}" + (f" {code}" if code else "") + (f" - {_scrub(message, self._secret)}" if message else "")
        if status in (408, 425, 429) or status >= 500:
            return IdentityUnavailable(f"aios-identity cannot issue a token right now: {detail}", http_status=status)
        hint = " - check AIOS_FLOW_IDENTITY_URL (is the /identity prefix missing?)" if status == 404 else ""
        return AuthError(
            f"aios-identity refused the credentials of {self.username}: {detail}{hint}",
            code=code or f"http_{status}",
            source="aios-identity",
            http_status=status,
        )


# -- process-wide provider, built from the environment ------------------------------------------------------------------------------------------------------

_provider: IdentityTokenProvider | None = None
_provider_lock = threading.Lock()


def get_provider(env: Mapping[str, str] | None = None) -> IdentityTokenProvider | None:
    """The provider the environment describes, or None when authentication is not configured (AIOS_FLOW_IDENTITY_URL unset or blank).

    The environment is read on every call, so a changed variable takes effect; an unchanged configuration reuses one provider (and its cached token).
    Raises AuthError when the URL is set but the configuration cannot work (empty secret, http to a non-loopback host)."""
    env = os.environ if env is None else env
    url = (env.get(ENV_URL) or "").strip()
    if not url:
        return None
    secret = (env.get(ENV_SECRET) or "").strip("\r\n")
    if not secret.strip():
        raise AuthError(
            f"{ENV_URL} is set but {ENV_SECRET} is empty: aios-flow authentication is half configured "
            "(macOS: add it to the login Keychain, see scripts/bridge_with_keychain.sh)",
            code="missing_secret",
            source="config",
        )
    username = (env.get(ENV_USER) or "").strip() or DEFAULT_USERNAME
    global _provider
    with _provider_lock:
        if _provider is None or not _provider.matches(url, secret, username):
            _provider = IdentityTokenProvider(url, secret, username=username)
        return _provider


def reset_provider() -> None:
    """Forget the process-wide provider and its token (tests; a changed environment does not need it)."""
    global _provider
    with _provider_lock:
        _provider = None
