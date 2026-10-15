/**
 * Runs the REAL AOKP synthesis code on `inputs.json` and writes `golden.json` (inputs + the outputs AOKP produced).
 * Invoked by run_golden.sh with AOKP_DIR / AOKP_COMMIT / OUT in the environment. Nothing here re-implements AOKP logic: it only calls it.
 */
import { readFileSync, writeFileSync } from "node:fs"
import { createHash } from "node:crypto"
import { join } from "node:path"

const AOKP = process.env.AOKP_DIR!
const OUT = process.env.OUT!
const HERE = process.env.HERE!
const load = (rel: string) => import(join(AOKP, "src/runtime", rel))

async function main() {
  const linker = await load("synthesis/citation-linker.ts")
  const grounding = await load("synthesis/citation-grounding.ts")
  const suggest = await load("synthesis/suggestion-engine.ts")
  const synth = await load("synthesis/synthesizer.ts")
  const quality = await load("synthesis/quality-guard.ts")
  const bank = await load("locale/prompt-bank.ts")
  const stub = await import(join(HERE, "llm_chat_stub.ts"))
  const inputs = JSON.parse(readFileSync(join(HERE, "inputs.json"), "utf8"))

  const guard = async <T>(fn: () => Promise<T> | T): Promise<{ ok: T } | { error: string }> => {
    try { return { ok: await fn() } } catch (e) { return { error: String(e) } }
  }
  const mapEntries = (m: Map<number, unknown>) => Array.from(m.entries())

  const out: Record<string, unknown> = { format: 1, aokp_commit: process.env.AOKP_COMMIT, node: process.version }

  out.grounding = []
  for (const c of inputs.grounding) {
    const r = await guard(() => {
      if (c.mode === "explicit") return { report: grounding.verifyCitationGrounding(c.answer, c.citations, c.chunks) }
      const { citationMap } = linker.formatContextWithCitations(c.chunks)
      const used = linker.extractUsedCitations(c.answer, citationMap)
      return { used, report: grounding.verifyCitationGrounding(c.answer, used, c.chunks) }
    })
    ;(out.grounding as unknown[]).push({ ...c, out: r })
  }

  out.format_extract = []
  for (const c of inputs.format_extract) {
    const r = await guard(() => {
      const { formattedContext, citationMap } = linker.formatContextWithCitations(c.chunks)
      return { formattedContext, citationMap: mapEntries(citationMap), used: linker.extractUsedCitations(c.answer, citationMap) }
    })
    ;(out.format_extract as unknown[]).push({ ...c, out: r })
  }

  out.suggestions = []
  for (const c of inputs.suggestions) {
    ;(out.suggestions as unknown[]).push({ ...c, out: await guard(() => suggest.generateSuggestions(c.query, c.chunks)) })
  }

  out.parse = []
  for (const c of inputs.parse) {
    ;(out.parse as unknown[]).push({ ...c, out: await guard(() => synth.parseStructuredResponse(c.raw, c.locale)) })
  }

  out.quality = []
  for (const c of inputs.quality) {
    stub.__load([{ text: c.raw }])
    const r = await guard(() => quality.checkAnswerQuality(c.query, c.answer, c.locale, { maxRetries: 1, qualityCheckEnabled: true }))
    ;(out.quality as unknown[]).push({ ...c, out: r, calls: stub.__calls() })
  }

  out.scenarios = []
  for (const c of inputs.scenarios) {
    stub.__load(c.script)
    const r = await guard(() => (c.config ? synth.synthesizeAnswer(c.request, c.config) : synth.synthesizeAnswer(c.request)))
    ;(out.scenarios as unknown[]).push({ ...c, out: r, calls: stub.__calls(), unused_script_steps: 0 })
  }

  out.render = []
  for (const c of inputs.render) {
    ;(out.render as unknown[]).push({ ...c, out: await guard(() => bank.renderPrompt(bank[c.template], c.locale, c.vars ?? undefined)) })
  }

  // Constants that live as module-private literals in the TS source: evaluated FROM the source text (nothing retyped), so the Python data module is generated from them.
  const srcOf = (rel: string) => readFileSync(join(AOKP, "src/runtime", rel), "utf8")
  const evalLiteral = (code: string) => new Function("return (" + code + ")")()
  const between = (text: string, startMarker: string, endMarker: string) => {
    const i = text.indexOf(startMarker); if (i < 0) throw new Error("marker not found: " + startMarker)
    const j = text.indexOf(endMarker, i + startMarker.length); if (j < 0) throw new Error("end marker not found: " + endMarker)
    return text.slice(i + startMarker.length, j)
  }
  const sg = srcOf("synthesis/suggestion-engine.ts")
  const gr = srcOf("synthesis/citation-grounding.ts")
  const patterns = evalLiteral("[" + between(sg, "const TOPIC_PATTERNS: [string, RegExp][] = [", "\n]\n") + "]") as [string, RegExp][]
  out.constants = {
    topic_suggestions: evalLiteral("{" + between(sg, "const TOPIC_SUGGESTIONS: Record<string, Suggestion[]> = {", "\n}\n") + "}"),
    topic_patterns: patterns.map(([k, re]) => ({ topic: k, source: re.source, flags: re.flags })),
    generic_suggestions: evalLiteral("[" + between(sg, "if (suggestions.length === 0) {\n    suggestions.push(", "\n    )\n  }") + "]"),
    stopwords: Array.from(evalLiteral("new Set([" + between(gr, "const STOPWORDS = new Set([", "])") + "])") as Set<string>),
    thresholds: { grounded: 0.18, weak: 0.08 },
  }

  // The prompt texts themselves (the Python bank is GENERATED from these, and a test pins its sha256).
  const prompts: Record<string, { vi: string; en: string }> = {}
  for (const name of ["SYNTHESIS_SYSTEM_PROMPT", "SYNTHESIS_USER_PROMPT", "QUALITY_CHECK_PROMPT"]) prompts[name] = { vi: bank[name].vi, en: bank[name].en }
  out.prompts = prompts
  out.prompt_sha256 = Object.fromEntries(Object.entries(prompts).map(([k, v]) => [k, { vi: createHash("sha256").update(v.vi, "utf8").digest("hex"), en: createHash("sha256").update(v.en, "utf8").digest("hex") }]))

  writeFileSync(OUT, JSON.stringify(out) + "\n")
  const errs = Object.entries(out).filter(([, v]) => Array.isArray(v)).map(([k, v]) => [k, (v as { out?: { error?: string } }[]).filter((x) => x.out && "error" in x.out).length])
  console.log("golden written:", OUT, "| cases with a thrown error per section:", JSON.stringify(errs))
}

main().catch((e) => { console.error(e); process.exit(1) })
