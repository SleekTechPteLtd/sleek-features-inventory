#!/usr/bin/env python3
"""
Regenerate domain-clm.html from clm/feature-set/**/*.md master sheets.

Groups the Canonical Feature Matrix by primary repository (see PRIMARY_REPO_ORDER),
then by CLM theme (see CLM_THEME_RULES): e.g. invoices, subscriptions, credit notes,
payments, offboarding, upgrades/downgrades.

Each row links to the inventory markdown via viewer.html. Repository columns
show ✓ when the Service / Repository field mentions that repo (substring match).
"""

from __future__ import annotations

import html
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Repo matrix columns: (header_abbr, canonical id, substring needles — case-insensitive)
REPO_COLUMNS: list[tuple[str, str, tuple[str, ...]]] = [
    ("SBF", "sleek-billings-frontend", ("sleek-billings-frontend",)),
    ("SBB", "sleek-billings-backend", ("sleek-billings-backend", "sleek-billings-api")),
    ("SDS", "sleek-service-delivery-api", ("sleek-service-delivery-api", "sleek-service-delivery")),
    ("SW", "sleek-website", ("sleek-website",)),
    ("CB", "customer-billing", ("customer-billing",)),
]

# Section grouping order (backend before frontend; independent of column order)
PRIMARY_REPO_ORDER: list[str] = [
    "sleek-billings-backend",
    "sleek-billings-frontend",
    "sleek-service-delivery-api",
    "sleek-website",
    "customer-billing",
    "other",
]

# CLM theme: (id, subsection heading, substring needles on title + path).
# First match wins — keep more specific themes before broader ones.
CLM_THEME_RULES: list[tuple[str, str, tuple[str, ...]]] = [
    (
        "offboarding",
        "Offboarding & onboarding",
        ("offboarding", "onboarding", "archive-company", "offboarding-request"),
    ),
    ("xero", "Xero integration", ("xero",)),
    (
        "upgrades",
        "Upgrades & downgrades",
        ("upgrade", "downgrade", "proration", "/upgrades/"),
    ),
    (
        "credit_notes",
        "Credit notes",
        ("credit-note", "credit note", "credit_notes", "credit-notes-to", "/credit-notes"),
    ),
    (
        "subscriptions",
        "Subscriptions",
        ("subscription", "auto-renew", "/subscription", "renewal reminder"),
    ),
    (
        "payments",
        "Payment requests & checkout",
        (
            "payment",
            "stripe",
            "checkout",
            "pay invoice",
            "credit card",
            "add card",
            "payment-token",
            "/payment-",
            "/stripe",
            "webhook",
        ),
    ),
    (
        "coupons_credits",
        "Coupons & credit balance",
        ("coupon", "discount", "credit balance", "/credit-balance", "/coupons"),
    ),
    (
        "invoices",
        "Invoices & billing documents",
        ("invoice", "invoic", "/invoice/", "/invoices"),
    ),
]

CLM_THEME_ORDER: list[str] = [t[0] for t in CLM_THEME_RULES] + ["other"]

_CLM_DIR = Path(__file__).resolve().parent
ROOT = _CLM_DIR.parent
FEATURE_ROOT = _CLM_DIR / "feature-set"
OUT_PATH = ROOT / "domain-clm.html"

FEATURE_NAME_RE = re.compile(
    r"^\|\s*\*\*Feature Name\*\*\s*\|\s*([^|]+)\|\s*$", re.MULTILINE
)
SERVICE_REPO_RE = re.compile(
    r"^\|\s*\*\*Service / Repository\*\*\s*\|\s*([^|]+)\|\s*$", re.MULTILINE
)
CRITICALITY_RE = re.compile(
    r"^\|\s*\*\*Criticality\*\*\s*\|\s*([^|]+)\|\s*$", re.MULTILINE
)
H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def parse_md(path: Path) -> tuple[str, str, str, bool]:
    text = path.read_text(encoding="utf-8")
    fm = FEATURE_NAME_RE.search(text)
    sr = SERVICE_REPO_RE.search(text)
    cr = CRITICALITY_RE.search(text)
    feature_name = fm.group(1).strip() if fm else ""
    service_repo = sr.group(1).strip() if sr else ""
    critical_high = (
        cr.group(1).strip().lower() == "high" if cr else False
    )
    title = feature_name
    if not title:
        hm = H1_RE.search(text)
        title = hm.group(1).strip() if hm else path.stem.replace("-", " ").title()
    rel = path.relative_to(ROOT).as_posix()
    return title, service_repo, rel, critical_high


def repo_flags(service_blob: str) -> list[bool]:
    blob = service_blob.lower()
    out: list[bool] = []
    for _abbr, _tip, needles in REPO_COLUMNS:
        hit = any(n.lower() in blob for n in needles)
        out.append(hit)
    return out


def primary_repo(service_blob: str) -> str:
    blob = service_blob.lower()
    key_by_id = {c[1]: c for c in REPO_COLUMNS}
    for key in PRIMARY_REPO_ORDER:
        if key == "other":
            return "other"
        _a, _tip, needles = key_by_id[key]
        if any(n.lower() in blob for n in needles):
            return key
    return "other"


def section_title(repo_key: str) -> str:
    if repo_key == "other":
        return "Other / unmatched repository"
    labels = {
        "sleek-service-delivery-api": "Sleek Service Delivery API",
        "sleek-billings-backend": "Sleek Billings Backend",
        "sleek-billings-frontend": "Sleek Billings Frontend",
        "sleek-website": "Sleek Website",
        "customer-billing": "Customer Billing",
    }
    return labels.get(repo_key, repo_key.replace("-", " ").title())


def clm_theme_id(title: str, rel: str) -> str:
    blob = f"{title} {rel}".lower().replace("\\", "/")
    for key, _label, needles in CLM_THEME_RULES:
        if any(n in blob for n in needles):
            return key
    return "other"


def theme_heading(theme_id: str) -> str:
    for key, label, _ in CLM_THEME_RULES:
        if key == theme_id:
            return label
    return "Other CLM topics"


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def td_check(hit: bool) -> str:
    if hit:
        return '<td style="text-align:center;padding:5px 10px;color:#a6f2cd;">✓</td>'
    return '<td style="text-align:center;padding:5px 10px;color:#9db0d7;">—</td>'


def build_matrix_rows(features: list[dict]) -> str:
    by_primary: dict[str, list[dict]] = defaultdict(list)
    for f in features:
        by_primary[f["primary"]].append(f)
    parts: list[str] = []
    keys_ordered = [k for k in PRIMARY_REPO_ORDER if k in by_primary]
    colspan = 1 + len(REPO_COLUMNS) + 3
    for repo_key in keys_ordered:
        rows = by_primary[repo_key]
        by_theme: dict[str, list[dict]] = defaultdict(list)
        for f in rows:
            tid = clm_theme_id(f["title"], f["rel"])
            by_theme[tid].append(f)
        parts.append(
            f'<tr class="fm-matrix-repo"><td colspan="{colspan}" style="padding:6px 10px;background:#0a1325;'
            f'color:#7a9cd4;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.06em;">'
            f"{esc(section_title(repo_key))}</td></tr>"
        )
        for theme_id in CLM_THEME_ORDER:
            if theme_id not in by_theme:
                continue
            theme_rows = sorted(by_theme[theme_id], key=lambda x: x["title"].lower())
            parts.append(
                f'<tr class="fm-matrix-theme"><td colspan="{colspan}" style="padding:5px 10px 5px 22px;'
                f'background:#0e1828;color:#9dafc6;font-weight:600;font-size:10px;'
                f'border-top:1px solid #1a2744;">{esc(theme_heading(theme_id))}</td></tr>'
            )
            for f in theme_rows:
                viewer = f'./viewer.html?file={esc(f["rel"])}'
                cap_cell = (
                    f'<td style="padding:5px 10px;color:#dbe7ff;">'
                    f'<a href="{viewer}">{esc(f["title"])}</a></td>'
                )
                checks = "".join(td_check(x) for x in f["flags"])
                parts.append(
                    f'<tr style="border-bottom:1px solid #1e2d4a;">{cap_cell}{checks}</tr>'
                )
    return "\n".join(parts)


def build_html(features: list[dict]) -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    n = len(features)
    high_crit = sum(1 for f in features if f.get("critical_high"))
    matrix_th = "".join(
        f'<th style="text-align:center;padding:6px 10px;color:#b7caf2;font-weight:600;" '
        f'title="{esc(tip)}">{abbr}</th>'
        for abbr, tip, _ in REPO_COLUMNS
    )
    matrix_body = build_matrix_rows(features)

    # Optional: topic-style summary by primary repo (compact)
    repo_counts: dict[str, int] = defaultdict(int)
    for f in features:
        repo_counts[f["primary"]] += 1
    summary_pills = "".join(
        f'<span class="pill">{esc(section_title(k))}: {v}</span>'
        for k, v in sorted(repo_counts.items(), key=lambda x: (-x[1], x[0]))
    )

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Sleek Features Inventory - CLM (Customer Lifecycle Management)</title>
    <style>
      :root {{ --bg:#0b1220; --panel:#121a2b; --line:#2a3757; --text:#e6ecfb; --muted:#9db0d7; }}
      * {{ box-sizing: border-box; }} body {{ margin:0; font-family: Inter, Arial, sans-serif; background:var(--bg); color:var(--text); }}
      .wrap {{ max-width:1100px; margin:0 auto; padding:24px 16px 40px; }} .panel {{ background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:14px; margin-bottom:20px; }}
      .menu {{ display:flex; gap:8px; flex-wrap:wrap; margin:10px 0 20px; }} .menu a {{ padding:6px 10px; border-radius:999px; border:1px solid var(--line); background:#101a2f; color:#c9d9fa; text-decoration:none; font-size:13px; }}
      .menu a.active {{ border-color:#5a8dde; background:#162747; color:#e5efff; }} .muted {{ color:var(--muted); }}
      .pill {{ display:inline-block; padding:2px 10px; border-radius:999px; font-size:12px; border:1px solid #2f7e59; background:#143a2a; color:#a6f2cd; }}
      .pill-row {{ display:flex; gap:8px; flex-wrap:wrap; margin-top:8px; }}
      a {{ color:#9dc5ff; text-decoration:none; }}
      /* Feature Matrix Annotations (aligned with domain-accounting.html) */
      .fm-toolbar {{ display:flex; align-items:center; gap:8px; margin-bottom:10px; }}
      .fm-toolbar h3 {{ margin:0; flex:1; font-size:1rem; color:#b7caf2; }}
      .fm-btn {{ padding:4px 12px; border-radius:6px; border:1px solid var(--line); background:#101d36; color:#c9d9fa; font-size:12px; cursor:pointer; }}
      .fm-btn:hover {{ border-color:#5a8dde; color:#e5efff; }}
      .fm-btn.primary {{ border-color:#2f7e59; background:#143a2a; color:#a6f2cd; }}
      .fm-priority-select {{ font-size:11px; background:#0c1629; border:1px solid #304a77; border-radius:4px; color:#c9d9fa; padding:2px 4px; }}
      .fm-priority-select.p-high   {{ border-color:#f97316; color:#f97316; }}
      .fm-priority-select.p-medium {{ border-color:#facc15; color:#facc15; }}
      .fm-priority-select.p-low    {{ border-color:#60a5fa; color:#60a5fa; }}
      .fm-notes {{ font-size:11px; background:#0c1629; border:1px solid #304a77; border-radius:4px; color:#c9d9fa; padding:3px 5px; width:100%; min-width:120px; resize:vertical; font-family:inherit; }}
      .fm-fp-check {{ accent-color:#f97316; width:14px; height:14px; cursor:pointer; }}
      tr.fm-fp-row td:first-child {{ text-decoration:line-through; opacity:0.5; }}
      tr.fm-fp-row {{ opacity:0.55; }}
    </style>
  </head>
  <body>
    <div class="wrap">
      <h1>CLM Domain (Customer Lifecycle Management)</h1>
      <p class="muted">Generated from <code>clm/feature-set/**/*.md</code>. Matrix columns are repositories mentioned in each feature&rsquo;s <strong>Service / Repository</strong> field. Rows are grouped by <em>primary</em> repository (first match in priority order: backend → frontend → service-delivery → …), then by <em>CLM theme</em> (keyword match on feature title and file path — edit <code>CLM_THEME_RULES</code> in <code>generate-clm-domain-html.py</code> to adjust).</p>
      <nav class="menu">
        <a href="./roadmap-scope-visual.html">Overview</a><a href="./domain-platform.html">Platform</a><a class="active" href="./domain-clm.html">CLM (Customer Lifecycle Management)</a><a href="./domain-compliance.html">Compliance</a><a href="./domain-corpsec.html">CorpSec</a><a href="./domain-accounting.html">Accounting</a>
      </nav>
      <section class="panel"><strong>Domain inventory:</strong> markdown under <code>clm/feature-set/</code> (run <code>clm/generate-clm-domain-html.py</code> after adding or editing features).</section>
      <section class="panel"><strong>Inventory counts:</strong><div class="pill-row"><span class="pill">Features: {n}</span><span class="pill">High criticality (master sheet): {high_crit}</span></div><div class="pill-row" style="margin-top:10px">{summary_pills}</div></section>
      <p class="muted" style="font-size:12px;">Regenerated: {esc(generated)}</p>

      <section class="panel" id="matrix-panel">
        <div class="fm-toolbar">
          <h3>Canonical Feature Matrix (by repository &amp; theme)</h3>
        </div>
        <p style="margin:0 0 14px;font-size:12px;color:var(--muted);">SBF = Sleek Billings Frontend · SBB = Sleek Billings Backend · SDS = Service Delivery API · SW = Sleek Website · CB = Customer Billing. A check means the inventory row cites that codebase.</p>
        <table id="feature-matrix" style="width:100%;border-collapse:collapse;font-size:12px;">
          <thead>
            <tr style="border-bottom:1px solid var(--line);">
              <th style="text-align:left;padding:6px 10px;color:#b7caf2;font-weight:600;">Capability</th>
              {matrix_th}
              <th style="text-align:center;padding:6px 10px;color:#b7caf2;font-weight:600;">Priority</th>
              <th style="text-align:left;padding:6px 10px;color:#b7caf2;font-weight:600;">Notes</th>
              <th style="text-align:center;padding:6px 10px;color:#b7caf2;font-weight:600;" title="False positive — mark if this row shouldn't be here">FP</th>
            </tr>
          </thead>
          <tbody>
            {matrix_body}
          </tbody>
        </table>
      </section>
    </div>
    <script>
      (function () {{
        const table  = document.getElementById('feature-matrix');
        if (!table) return;
        const tbody  = table.querySelector('tbody');
        let rowId = 0;
        for (const tr of tbody.rows) {{
          const first = tr.cells[0];
          if (first && first.colSpan > 1) {{
            if (tr.classList.contains('fm-matrix-repo')) {{
              tr.dataset.category = first.textContent.trim();
            }} else if (tr.classList.contains('fm-matrix-theme')) {{
              tr.dataset.subtheme = first.textContent.trim();
            }}
            continue;
          }}
          tr.dataset.rowId = rowId++;
          const tdPri  = tr.insertCell(-1);
          const tdNote = tr.insertCell(-1);
          const tdFp   = tr.insertCell(-1);
          tdPri.style.cssText  = 'text-align:center;padding:4px 8px;vertical-align:middle;';
          tdNote.style.cssText = 'padding:4px 8px;vertical-align:middle;';
          tdFp.style.cssText   = 'text-align:center;padding:4px 8px;vertical-align:middle;';
          const sel = document.createElement('select');
          sel.className = 'fm-priority-select';
          sel.innerHTML = '<option value="">—</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option>';
          sel.dataset.row = tr.dataset.rowId;
          tdPri.appendChild(sel);
          const ta = document.createElement('textarea');
          ta.className = 'fm-notes';
          ta.rows = 1;
          ta.placeholder = 'notes…';
          ta.dataset.row = tr.dataset.rowId;
          tdNote.appendChild(ta);
          const cb = document.createElement('input');
          cb.type = 'checkbox';
          cb.className = 'fm-fp-check';
          cb.dataset.row = tr.dataset.rowId;
          tdFp.appendChild(cb);
        }}
        function applyFpStyle(tr, isFp) {{
          tr.classList.toggle('fm-fp-row', !!isFp);
        }}
        tbody.addEventListener('change', e => {{
          const el = e.target;
          if (el.classList.contains('fm-priority-select')) {{
            el.className = 'fm-priority-select' + (el.value ? ' p-' + el.value : '');
          }}
          if (el.classList.contains('fm-fp-check')) {{
            const tr = el.closest('tr');
            if (tr) applyFpStyle(tr, el.checked);
          }}
        }});
      }})();
    </script>
  </body>
</html>
"""


def main() -> int:
    if not FEATURE_ROOT.is_dir():
        print(f"Missing {FEATURE_ROOT}", file=sys.stderr)
        return 1
    paths = sorted(FEATURE_ROOT.rglob("*.md"))
    features: list[dict] = []
    for path in paths:
        title, service_repo, rel, critical_high = parse_md(path)
        flags = repo_flags(service_repo)
        pri = primary_repo(service_repo)
        features.append(
            {
                "title": title,
                "service_repo": service_repo,
                "rel": rel,
                "flags": flags,
                "primary": pri,
                "critical_high": critical_high,
            }
        )

    OUT_PATH.write_text(build_html(features), encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(features)} features)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
