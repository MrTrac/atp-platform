# Local Bootstrap

Bootstrap local cho ATP M1-M2 tren macOS:

1. vao repo `SOURCE_DEV/platforms/ATP`
2. kiem tra `python3 --version`
3. chay `make help`
4. chay `make smoke`
5. chay `make test`

CLI seed co san:

- `./cli/atp validate tests/fixtures/requests/sample_request.yaml`
- `./cli/atp run tests/fixtures/requests/sample_request.yaml`
- `./cli/atp inspect`

Luu y van hanh:

- khong tao runtime artifact trong repo ATP
- khong point artifact output sang sibling repo trong M1-M2
- `run` hien tai chi la preview flow, khong execute ATP full pipeline
