#!/usr/bin/env python3
"""
Regenerate domain-clm.html from clm/feature-set/**/*.md master sheets.

Some top-level feature-set folders are skipped (see EXCLUDED_FEATURE_SET_SUBDIRS).
Decoded screenshot routes can be skipped in the surface gallery only (see EXCLUDED_CLM_GALLERY_ROUTES).

Groups the Canonical Feature Matrix by primary repository (see PRIMARY_REPO_ORDER),
then by CLM theme (see CLM_THEME_RULES): e.g. invoices, subscriptions, credit notes,
payments, offboarding, upgrades/downgrades.

Each row links to the inventory markdown via viewer.html. Repository columns
show ✓ when the Service / Repository field mentions that repo (substring match).

UI screenshots live under by-surface/clm/screenshots/ (see
scripts/capture-clm-screenshots.mjs). Filenames are {md-stem}__*.png in the same
subfolder layout as clm/feature-set/.

The generated page lists screenshots in three panels (same layout as
domain-corpsec.html): Billing portal (Sleek Billings admin SPA), Admin app
(admin-sit.sleek.sg), and Customer app (client-facing). Classification uses the
route embedded in the filename plus Service / Repository metadata.
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
# Playwright captures: by-surface/clm/screenshots/<same dirs as feature-set>/{stem}__*.png
SCREENSHOTS_ROOT = ROOT / "by-surface" / "clm" / "screenshots"
OUT_PATH = ROOT / "domain-clm.html"

# Top-level folder under clm/feature-set/ to omit from domain-clm.html (matrix + gallery).
# Maps user-facing routes / areas to inventory directory names, e.g. subscription-config/edit →
# subscription-config-form, /admin/invoices/reconcile → admin-invoices-reconcile.
EXCLUDED_FEATURE_SET_SUBDIRS: frozenset[str] = frozenset(
    {
        "admin-incomplete-orders",
        "admin-invoices-reconcile",
        "admin-invoices-update-services",
        "admin-new-coupons",
        "admin-new-coupons-create-edit",
        "admin-paid-incomplete-orders",
        "admin-subscriptions-paid",
        "admin-subscriptions-paid-edit",
        "admin-subscriptions-unpaid",
        "admin-transactions",
        "coupons-form",
        "credit-balance",
        "deliverables-analytics",
        "delivery-config-form",
        "external-invoice",
        "onboarding",
        "overview",
        "payments",
        "subscription-config-form",
        "xero-config-monitoring",
        "xero-webhook",
    }
)

# SPA routes recovered from screenshot filenames (see route_from_clm_screenshot_href) omitted
# from the three-surface gallery only. Use when the same inventory row has multiple captures
# (e.g. list vs edit) but edit should not appear in domain-clm.html.
EXCLUDED_CLM_GALLERY_ROUTES: frozenset[str] = frozenset(
    {
        "/subscription-config/edit",
        "/delivery-config/edit",
    }
)

# Same basenames as EXCLUDED_CLM_CAPTURE_REL_PATHS in scripts/capture-clm-screenshots.mjs — no gallery thumbs.
EXCLUDED_CLM_SCREENSHOT_MD_REL_PATHS: frozenset[str] = frozenset(
    {
        "payment-success/pay-subscription-billing-invoice.md",
    }
)

# Surface URLs (aligned with capture-clm-screenshots.mjs / domain-corpsec.html)
CLM_BILLINGS_PORTAL_URL = "https://sg-billings-sit.sleek.com/"
CLM_ADMIN_APP_URL = "https://admin-sit.sleek.sg"
CLM_CUSTOMER_APP_URL = "https://sg-app-sit.sleek.com"

# SVG for empty thumbnail (matches domain-corpsec.html placeholder)
_CE_PLACEHOLDER_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" '
    'stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">'
    '<rect x="3" y="5" width="18" height="14" rx="2"/>'
    '<circle cx="8.5" cy="10.5" r="1.5"/><path d="m21 15-5-5L5 19"/></svg>'
)

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


def feature_set_first_segment(repo_rel: str) -> str | None:
    """First directory under clm/feature-set/ for a repo-root-relative path."""
    p = repo_rel.replace("\\", "/")
    prefix = "clm/feature-set/"
    if not p.startswith(prefix):
        return None
    rest = p[len(prefix) :].strip("/")
    if not rest:
        return None
    return rest.split("/")[0]


def is_excluded_feature_md(repo_rel: str) -> bool:
    seg = feature_set_first_segment(repo_rel)
    return seg is not None and seg in EXCLUDED_FEATURE_SET_SUBDIRS


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


def screenshot_paths_for_feature_md(md_path: Path) -> list[Path]:
    """
    PNGs captured for this feature markdown (same naming as capture-clm-screenshots.mjs).
    Returns repo-root-relative paths under by-surface/clm/screenshots/.
    """
    try:
        rel = md_path.relative_to(FEATURE_ROOT)
    except ValueError:
        return []
    if rel.as_posix() in EXCLUDED_CLM_SCREENSHOT_MD_REL_PATHS:
        return []
    stem = md_path.stem
    sub = rel.parent.as_posix()
    shot_dir = SCREENSHOTS_ROOT / sub if sub != "." else SCREENSHOTS_ROOT
    if not shot_dir.is_dir():
        return []
    return sorted(shot_dir.glob(f"{stem}__*.png"))


def screenshot_urls_for_feature_md(md_path: Path) -> list[str]:
    """Paths relative to domain-clm.html (repo root) for use as img src / href."""
    return [p.relative_to(ROOT).as_posix() for p in screenshot_paths_for_feature_md(md_path)]


def route_from_clm_screenshot_href(href: str) -> str:
    """Recover SPA path from capture filename: {stem}__a__b__c.png -> /a/b/c."""
    base = Path(href).stem
    # capture-clm-screenshots.mjs: company-billing routes encode tab in filename (-tab0, -tab1, …).
    if "company-billing" in base.lower():
        if "-tab" in base:
            m = re.search(r"-tab(\d+)", base)
            tab = m.group(1) if m else "0"
            return f"/admin/company-billing?tab={tab}"
        return "/admin/company-billing"
    parts = base.split("__")
    if len(parts) < 2:
        return "/"
    return "/" + "/".join(parts[1:])


def clm_gallery_bucket(route: str, service_repo: str, primary: str) -> str:
    """
    Classify screenshot for gallery panels: admin | customer | billing.
    Mirrors capture-clm-screenshots.mjs resolveSurface where possible.
    """
    r = route.lower()
    sr = service_repo.lower()
    if r.startswith("/admin"):
        return "admin"
    if primary in ("customer-billing", "sleek-website"):
        return "customer"
    if "customer-billing" in sr or "sleek-website" in sr:
        return "customer"
    if "/customer" in r or r.startswith("/checkout"):
        return "customer"
    return "billing"


def collect_gallery_items(features: list[dict]) -> dict[str, list[dict]]:
    """Bucket -> list of {theme_id, title, href_img, rel, route}."""
    buckets: dict[str, list[dict]] = {"billing": [], "admin": [], "customer": []}
    for f in features:
        for href in f.get("screenshots") or []:
            route = route_from_clm_screenshot_href(href)
            if route.lower() in EXCLUDED_CLM_GALLERY_ROUTES:
                continue
            b = clm_gallery_bucket(route, f["service_repo"], f["primary"])
            tid = clm_theme_id(f["title"], f["rel"])
            buckets[b].append(
                {
                    "theme_id": tid,
                    "title": f["title"],
                    "href_img": href,
                    "rel": f["rel"],
                    "route": route,
                }
            )
    return buckets


def build_ce_gallery_sections(features: list[dict]) -> str:
    """Three ce-panels: billing portal admin, admin app, customer app (corpsec-style)."""
    buckets = collect_gallery_items(features)
    panels: list[tuple[str, str, str, str, str]] = [
        (
            "billing",
            "Billing portal (Sleek Billings admin)",
            CLM_BILLINGS_PORTAL_URL,
            "sg-billings-sit.sleek.com",
            "Internal staff billing &amp; delivery SPA (sleek-billings-frontend). "
            "Screenshots from <code>by-surface/clm/screenshots/</code> keyed to inventory routes.",
        ),
        (
            "admin",
            "Admin app",
            CLM_ADMIN_APP_URL,
            "admin-sit.sleek.sg",
            "Internal admin app routes under <code>/admin/…</code> (invoices, coupons, subscriptions, analytics).",
        ),
        (
            "customer",
            "Customer app",
            CLM_CUSTOMER_APP_URL,
            "sg-app-sit.sleek.com",
            "Client-facing surfaces (customer billing, website) when cited in inventory.",
        ),
    ]
    out: list[str] = []
    for key, h2_title, base_url, url_label, blurb in panels:
        items = buckets[key]
        sections_inner = _build_ce_theme_sections(items)
        empty_note = ""
        if not items:
            empty_note = (
                '<p class="muted" style="margin:0 0 12px;font-size:12px;">'
                "No screenshots classified for this surface yet. "
                "Run <code>scripts/capture-clm-screenshots.mjs</code> after exporting localStorage, "
                "or add inventory rows that cite customer-billing / admin routes.</p>"
            )
        out.append(
            f"""      <section class="panel ce-panel" id="clm-gallery-{esc(key)}">
        <h2>{esc(h2_title)} — <a href="{esc(base_url)}" target="_blank" rel="noopener" style="font-weight:400;">{esc(url_label)}</a></h2>
        <p style="margin:0 0 12px;font-size:12px;color:var(--muted);">{blurb}</p>
        {empty_note}
        <div class="ce-section-grid">
          <div class="ce-col" style="flex:1;min-width:0;">
            {sections_inner}
          </div>
        </div>
      </section>"""
        )
    return "\n".join(out)


def _build_ce_theme_sections(items: list[dict]) -> str:
    if not items:
        return ""
    by_theme: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        by_theme[it["theme_id"]].append(it)
    parts: list[str] = []
    for theme_id in CLM_THEME_ORDER:
        if theme_id not in by_theme:
            continue
        rows = sorted(
            by_theme[theme_id],
            key=lambda x: (x["title"].lower(), x["route"]),
        )
        tlabel = theme_heading(theme_id)
        n = len(rows)
        cards: list[str] = []
        for it in rows:
            viewer = f'./viewer.html?file={esc(it["rel"])}'
            r = it["route"]
            route_short = r if len(r) <= 56 else r[:53] + "…"
            img = esc(it["href_img"])
            cards.append(
                f'<div class="ce-card">'
                f'<div class="ce-thumb">'
                f'<a href="{img}" target="_blank" rel="noopener">'
                f'<img src="{img}" alt="{esc(it["title"])}" loading="lazy" '
                f"onerror=\"this.closest('.ce-thumb').classList.add('no-img')\" />"
                f"</a>"
                f'<div class="ce-no-img">{_CE_PLACEHOLDER_SVG}<span>no screenshot</span></div>'
                f"</div>"
                f'<div class="ce-card-label"><a href="{viewer}">{esc(it["title"])}</a>'
                f'<span class="muted" style="font-size:10px;display:block;margin-top:3px;">{esc(route_short)}</span>'
                f"</div>"
                f"</div>"
            )
        parts.append(
            f"""            <div class="ce-section">
              <div class="ce-section-header">
                <span class="ce-section-title">{esc(tlabel)}</span>
                <span class="ce-section-count">{n} screenshot{'s' if n != 1 else ''}</span>
              </div>
              <div class="ce-feature-list">
                {"".join(cards)}
              </div>
            </div>"""
        )
    return "\n".join(parts)


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
    colspan = 1 + len(REPO_COLUMNS) + 3  # capability + repos + priority/notes/fp
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
    gallery_sections = build_ce_gallery_sections(features)

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
      /* Screenshot gallery (aligned with domain-corpsec.html) */
      .ce-panel {{ margin-bottom: 20px; }}
      .ce-panel h2 {{ margin: 0 0 4px; font-size: 1rem; color: #b7caf2; }}
      .ce-panel > p {{ margin: 0 0 16px; font-size: 12px; color: var(--muted); }}
      .ce-section-grid {{ display: flex; gap: 12px; align-items: flex-start; }}
      .ce-col {{ flex: 1; display: flex; flex-direction: column; gap: 12px; }}
      @media (max-width: 720px) {{ .ce-section-grid {{ flex-direction: column; }} .ce-col {{ width: 100%; }} }}
      .ce-section {{ background: #0d1728; border: 1px solid var(--line); border-radius: 10px; padding: 12px; }}
      .ce-section-header {{ display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 2px; }}
      .ce-section-title {{ font-size: 13px; font-weight: 600; color: #dbe8ff; }}
      .ce-section-count {{ font-size: 11px; color: var(--muted); }}
      .ce-feature-list {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }}
      @media (max-width: 500px) {{ .ce-feature-list {{ grid-template-columns: 1fr; }} }}
      .ce-card {{ background: #101d36; border: 1px solid #243352; border-radius: 7px; overflow: hidden; }}
      .ce-thumb {{ position: relative; width: 100%; aspect-ratio: 16/7; background: #0c1629; border-bottom: 1px solid #1e304f; overflow: hidden; display: flex; align-items: center; justify-content: center; }}
      .ce-thumb a {{ display: block; width: 100%; height: 100%; }}
      .ce-thumb img {{ width: 100%; height: 100%; object-fit: cover; object-position: top; display: block; transition: opacity 0.15s; }}
      .ce-thumb.no-img img {{ display: none; }}
      .ce-no-img {{ display: none; flex-direction: column; align-items: center; gap: 4px; color: #3d5a8a; font-size: 11px; }}
      .ce-thumb.no-img .ce-no-img {{ display: flex; }}
      .ce-no-img svg {{ opacity: 0.45; }}
      .ce-card-label {{ padding: 6px 8px; font-size: 11px; color: #a0b8e0; line-height: 1.35; }}
      .ce-card-label a {{ color: #c9d9fa; }}
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
      <p class="muted">Generated from <code>clm/feature-set/**/*.md</code>. <strong>UI screenshots</strong> are grouped by surface below (billing portal, admin app, customer app), similar to <a href="./domain-corpsec.html">domain-corpsec.html</a>. The matrix lists repositories mentioned in each feature&rsquo;s <strong>Service / Repository</strong> field; rows are grouped by <em>primary</em> repository, then by <em>CLM theme</em> (edit <code>CLM_THEME_RULES</code> in <code>generate-clm-domain-html.py</code> to adjust).</p>
      <nav class="menu">
        <a href="./roadmap-scope-visual.html">Overview</a><a href="./domain-platform.html">Platform</a><a class="active" href="./domain-clm.html">CLM (Customer Lifecycle Management)</a><a href="./domain-compliance.html">Compliance</a><a href="./domain-corpsec.html">CorpSec</a><a href="./domain-accounting.html">Accounting</a>
      </nav>
      <section class="panel"><strong>Domain inventory:</strong> markdown under <code>clm/feature-set/</code> (run <code>clm/generate-clm-domain-html.py</code> after adding or editing features). Screenshots live in <code>by-surface/clm/screenshots/</code> — generate with <code>scripts/capture-clm-screenshots.mjs</code>.</section>
      <section class="panel"><strong>Inventory counts:</strong><div class="pill-row"><span class="pill">Features: {n}</span><span class="pill">High criticality (master sheet): {high_crit}</span></div><div class="pill-row" style="margin-top:10px">{summary_pills}</div></section>
      <p class="muted" style="font-size:12px;">Regenerated: {esc(generated)}</p>

{gallery_sections}

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
        rel = path.relative_to(ROOT).as_posix()
        if is_excluded_feature_md(rel):
            continue
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
                "screenshots": screenshot_urls_for_feature_md(path),
            }
        )

    OUT_PATH.write_text(build_html(features), encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(features)} features)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
