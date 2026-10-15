/**
 * Scripted stand-in for AOKP `src/runtime/platform/llm-chat.ts`, used ONLY by make_golden.ts.
 *
 * `run_golden.sh` maps the import `@/src/runtime/platform/llm-chat` to this file (a tsconfig `paths` override), so the REAL AOKP synthesizer/quality-guard run unmodified
 * against a model whose every answer is scripted. Every call is recorded (role + content) so the Python port can be checked to send the SAME prompts in the SAME order.
 */
export type ChatMessage = { role: "system" | "user" | "assistant"; content: string }

type Step = { text: string } | { throw: string }

const state: { script: Step[]; calls: ChatMessage[][] } = { script: [], calls: [] }

export function __load(script: Step[]): void {
  state.script = script.slice()
  state.calls = []
}

export function __calls(): ChatMessage[][] {
  return state.calls
}

export async function llmChat(messages: ChatMessage[], ..._rest: unknown[]): Promise<string> {
  state.calls.push(messages.map((m) => ({ role: m.role, content: m.content })))
  const next = state.script.shift()
  if (!next) throw new Error("scripted LLM exhausted")
  if ("throw" in next) throw new Error(next.throw)
  return next.text
}
