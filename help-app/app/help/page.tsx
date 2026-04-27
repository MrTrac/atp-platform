import { HelpClient, type HelpSection, MarkdownPage } from "@aios/help-portal";
import { loadHelpContent } from "@aios/help-portal/server";
import { readFileSync } from "node:fs";
import { join } from "node:path";

function readVersion(): string {
  // ATP's VERSION lives at project root, two levels up from help-app/.
  try { return readFileSync(join(process.cwd(), "..", "VERSION"), "utf-8").trim(); }
  catch { return "unknown"; }
}

export default function HelpPage() {
  const version = readVersion();
  const content = loadHelpContent(process.cwd());
  const sections: HelpSection[] = [];
  for (const g of content.meta.groups) {
    for (const slug of g.items) {
      const page = content.pages.find((p) => p.slug === slug);
      if (!page) continue;
      sections.push({ id: page.frontmatter.id, title: page.frontmatter.title, group: `${g.icon ?? "📄"} ${g.label}` });
    }
  }
  return (
    <HelpClient sections={sections} version={version}>
      <h1 className="mb-3 text-2xl font-bold" style={{ color: "var(--shell-text-bright)" }}>ATP — Help</h1>
      <p className="mb-6 text-[13px] leading-relaxed" style={{ color: "var(--shell-text-muted)" }}>
        Autonomous Task Platform — 14-step transformation flow. Hiển thị <code>v{version}</code>.
      </p>
      {content.pages.map((p) => (
        <MarkdownPage
          key={p.slug}
          frontmatter={p.frontmatter}
          body={p.body}
          slug={p.slug}
          shotsCapturedAt={content.shotsCapturedAt}
          shotsBySlug={content.shotsBySlug}
        />
      ))}
    </HelpClient>
  );
}
