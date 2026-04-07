#!/usr/bin/env python3
"""
Regenerate domain-accounting.html from accounting/<module>/*.md inventory.

Usage (from repo root):
  python3 scripts/generate-accounting-domain-html.py
"""

from __future__ import annotations

import html
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def humanize_slug(slug: str) -> str:
    return " ".join(p.capitalize() for p in slug.replace("_", "-").split("-") if p)


def extract_h1(md_path: Path) -> str | None:
    try:
        text = md_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"warn: could not read {md_path}: {e}", file=sys.stderr)
        return None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return None


def link_title_from_file(md_path: Path) -> str:
    h1 = extract_h1(md_path)
    if h1:
        return h1
    stem = md_path.stem
    return humanize_slug(stem)


def emit_article(module_dir: Path, module_slug: str) -> str:
    md_files = sorted(module_dir.glob("*.md"))
    if not md_files:
        return ""

    display = humanize_slug(module_slug)
    lines: list[str] = []
    lines.append('        <article class="topic skip-feature-transform">')
    lines.append(f'          <h3 data-title="{html.escape(display, quote=True)}">{html.escape(display)}</h3>')
    folder_href = f"./accounting/{module_slug}/"
    lines.append(
        f'          <small class="muted">Inventory files: <a href="{html.escape(folder_href, quote=True)}">accounting/{html.escape(module_slug)}/</a></small>'
    )
    lines.append('          <div class="grid">')
    lines.append('            <section class="box" style="grid-column: 1 / -1;">')
    lines.append('              <h4>Features</h4>')
    lines.append(
        '              <ul style="column-count: 2; column-gap: 24px; font-size: 12px;">'
    )
    for md in md_files:
        rel = f"./accounting/{module_slug}/{md.name}"
        title = link_title_from_file(md)
        lines.append(
            f'              <li><a href="{html.escape(rel, quote=True)}">{html.escape(title)}</a></li>'
        )
    lines.append("              </ul>")
    lines.append("            </section>")
    lines.append("          </div>")
    lines.append("        </article>")
    return "\n".join(lines) + "\n"


def main() -> int:
    root = repo_root()
    accounting = root / "accounting"
    if not accounting.is_dir():
        print(f"error: missing {accounting}", file=sys.stderr)
        return 1

    module_dirs = sorted(
        p for p in accounting.iterdir() if p.is_dir() and not p.name.startswith(".")
    )

    blocks: list[str] = []
    for d in module_dirs:
        blocks.append(emit_article(d, d.name))

    generated = "".join(blocks)

    out_path = root / "domain-accounting.html"
    template_before = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Sleek Features Inventory - Accounting</title>
    <style>
      :root { --bg:#0b1220; --panel:#121a2b; --line:#2a3757; --text:#e6ecfb; --muted:#9db0d7; }
      * { box-sizing: border-box; } body { margin:0; font-family: Inter, Arial, sans-serif; background:var(--bg); color:var(--text); }
      .wrap { max-width:1100px; margin:0 auto; padding:24px 16px 40px; } .panel { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:14px; margin-bottom:20px; }
      .menu { display:flex; gap:8px; flex-wrap:wrap; margin:10px 0 20px; } .menu a { padding:6px 10px; border-radius:999px; border:1px solid var(--line); background:#101a2f; color:#c9d9fa; text-decoration:none; font-size:13px; }
      .menu a.active { border-color:#5a8dde; background:#162747; color:#e5efff; } .muted { color:var(--muted); } .topic { border:1px solid var(--line); border-radius:10px; padding:12px; background:#0f172b; margin-bottom:16px; } .topic:last-child { margin-bottom:0; }
      .pill { display:inline-block; padding:2px 10px; border-radius:999px; font-size:12px; border:1px solid #2f7e59; background:#143a2a; color:#a6f2cd; }
      .pill-row { display:flex; gap:8px; flex-wrap:wrap; margin-top:8px; }
      .subgrid { display:grid; gap:8px; }
      .subgrid h5 { margin:0; font-size:12px; color:#b7caf2; }

      .feature-row { display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
      .must-toggle { display:inline-flex; align-items:center; gap:6px; font-size:12px; color:#9db0d7; }
      .must-toggle input { position:absolute; opacity:0; pointer-events:none; }
      .checkmark { display:inline-flex; align-items:center; justify-content:center; width:18px; height:18px; border-radius:4px; border:1px solid #486089; color:#7f94b7; background:#101a2f; font-size:12px; }
      .must-toggle.is-on .checkmark { border-color:#2f7e59; background:#143a2a; color:#a6f2cd; }
      .must-toggle.is-on .must-text { color:#a6f2cd; }
      .feature-label { color:#dbe7ff; }
      .priority-pill { display:inline-block; padding:2px 8px; border-radius:999px; border:1px solid #43608c; background:#14223d; color:#bcd2f7; font-size:11px; }
      .grid { display:grid; gap:10px; grid-template-columns: repeat(2, minmax(0,1fr)); margin-top:10px; } .box { border:1px dashed #37507b; border-radius:8px; padding:10px; background:#101d36; min-height:110px; }
      .box h4 { margin:0 0 6px; font-size:13px; color:#c9d9fa; } .box ul { margin:0; padding-left:18px; color:#afc2e8; font-size:13px; } .editable { border:1px solid #304a77; border-radius:6px; padding:8px; background:#0c1629; min-height:54px; color:#d8e5ff; font-size:13px; }
      a { color:#9dc5ff; text-decoration:none; } @media (max-width: 880px) { .grid { grid-template-columns: 1fr; } }
    </style>
  </head>
  <body>
    <div class="wrap">
      <h1>Accounting Domain</h1>
      <p class="muted">Modules inside the `accounting/` TLD domain folder.</p>
      <nav class="menu">
        <a href="./roadmap-scope-visual.html">Overview</a><a href="./domain-platform.html">Platform</a><a href="./domain-clm.html">CLM</a><a href="./domain-compliance.html">Compliance</a><a href="./domain-corpsec.html">CorpSec</a><a class="active" href="./domain-accounting.html">Accounting</a>
      </nav>
      <section class="panel"><strong>Domain reference:</strong> <a href="./accounting/README.md">accounting/README.md</a></section>
      <section class="panel"><strong>Inventory counts:</strong><div class="pill-row"><span class="pill">Modules: <span id="moduleCount">0</span></span><span class="pill">Features: <span id="featureCount">0</span></span><span class="pill">Must-have: <span id="mustHaveCount">0</span></span></div></section>
      <p class="muted">Each module below links to markdown feature rows. Add a <code>[Must-have]</code> prefix on a list item to count it toward migration scope. Interactive must-have and priority labels apply only to modules that do not use the link-list layout.</p>
      <section class="panel">
      <!-- GENERATED_ACCOUNTING_TOPICS_START -->
"""

    template_after = """      <!-- GENERATED_ACCOUNTING_TOPICS_END -->
      </section>
    </div>
    <script>
      (function () {
        const modules = document.querySelectorAll(".topic");
        let totalFeatures = 0;
        let totalMustHave = 0;

        modules.forEach((moduleEl) => {
          const title = moduleEl.querySelector("h3");
          const listItems = moduleEl.querySelectorAll("ul li");

          if (moduleEl.classList.contains("skip-feature-transform")) {
            listItems.forEach((li) => {
              const raw = li.textContent.trim();
              if (/\\[Must-have\\]/i.test(raw)) totalMustHave += 1;
            });
            totalFeatures += listItems.length;
            if (title) {
              const base = title.getAttribute("data-title") || title.textContent.trim();
              title.innerHTML = `${base} <span class="pill">${listItems.length} features</span>`;
            }
            return;
          }

          listItems.forEach((li, idx) => {
            const raw = li.textContent.trim();
            const explicitMust = /\\[Must-have\\]/i.test(raw);
            const priorityMatch = raw.match(/\\[P([0-3])\\]/i);
            const priority = priorityMatch ? `P${priorityMatch[1]}` : idx === 0 ? "P1" : "P2";
            const mustHave = explicitMust || idx === 0;
            const cleaned = raw.replace(/\\[Must-have\\]/ig, "").replace(/\\[P[0-3]\\]/ig, "").trim();

            if (mustHave) totalMustHave += 1;

            li.innerHTML = `
              <div class="feature-row">
                <span class="must-toggle ${mustHave ? "is-on" : ""}">
                  <input type="checkbox" ${mustHave ? "checked" : ""} disabled />
                  <span class="checkmark">✓</span>
                  <span class="must-text">Must-have</span>
                </span>
                <span class="feature-label">${cleaned}</span>
                <span class="priority-pill">${priority}</span>
              </div>
            `;
          });

          const featureCount = listItems.length;
          totalFeatures += featureCount;
          if (title) title.innerHTML = `${title.textContent} <span class="pill">${featureCount} features</span>`;
        });

        const moduleCountEl = document.getElementById("moduleCount");
        const featureCountEl = document.getElementById("featureCount");
        const mustHaveCountEl = document.getElementById("mustHaveCount");
        if (moduleCountEl) moduleCountEl.textContent = modules.length;
        if (featureCountEl) featureCountEl.textContent = totalFeatures;
        if (mustHaveCountEl) mustHaveCountEl.textContent = totalMustHave;
      })();
    </script>

  </body>
</html>
"""

    full = template_before + generated + template_after
    out_path.write_text(full, encoding="utf-8")

    n_mod = sum(1 for b in blocks if b)
    n_feat = sum(len(list(d.glob("*.md"))) for d in module_dirs)
    print(f"wrote {out_path} ({n_mod} modules, {n_feat} feature files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
