#!/usr/bin/env python3
"""Generate corpsec/admin-app/*.md from Corpsec CSV (Admin App rows only)."""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "Corpsec - Sleek Feature Scope Audit Master Sheet - Sheet1.csv"
OUT_DIR = ROOT / "corpsec" / "admin-app"

# Feature name -> full custom evidence (replaces auto block)
EVIDENCE_OVERRIDE: dict[str, str] = {
    "Filter & Sort Company List": """### sleek-website

- `src/views/admin/companies/index.js` — Status / Client Type / Company Type / Record Type multi-selects, SG-only ACRA filters, column sort (`handleClickTableHeader`), inline name and registration-ID filters.

### sleek-back

- `controllers/admin/company-controller.js` — `GET /admin/companies` with `sortBy` / `sortOrder`, `createFindQuery` (status, sub_status, clientType, company_type, record_type, …).""",
    "Create Company – Incorporation": """### sleek-website

- `src/views/admin/companies/create-draft-company-button/create-draft-company-button.js` — draft creation (incorporation vs transfer; AU sole-trader variant where applicable).

### sleek-back

- `controllers/admin/company-controller.js` — `POST /admin/companies/draft-creation` (`companies`, `full`).""",
    "Create Company – Transfer": """### sleek-website

- `src/views/admin/companies/create-draft-company-button/create-draft-company-button.js` — Transfer path and AU variants.

### sleek-back

- `controllers/admin/company-controller.js` — `POST /admin/companies/draft-creation`.""",
}


def evidence_from_entry_point(ep: str, feature: str, deps: str) -> str:
    ep = ep or ""
    lines: list[str] = []

    if "Company Overview" in ep:
        lines.extend(
            [
                "### sleek-website",
                "",
                "- `src/views/admin/company-overview/index.js` — primary revamped overview (tabs: Overview, People & Entities, Shares, Accounting, Deadlines, etc.).",
                "- `src/views/admin/companies/edit/index.js` — legacy company edit (still linked from list when feature flags dictate).",
                "- People & Entities partials under `src/views/admin/companies/edit/` (e.g. directors, shareholders, secretaries, registrable controllers, HK SCR, AU trust/public officer sections).",
                "",
            ]
        )
    elif "Corp Sec" in ep and "AR Filing" in ep:
        lines.extend(
            [
                "### sleek-website",
                "",
                "- `src/views/admin/corpsec/ar-filing/index.js` and `components/*` — company selector, workflow selector, source documents, manual upload (`ManualUploadSection.js`). Webpack: `admin/corpsec/ar-filing`.",
                "",
                "### sleek-back",
                "",
                "- `controllers-v2/corpsec.js` + `controllers-v2/handlers/corpsec/ar-filing.js` — AR filing REST routes (documents, upload, process binding).",
                "",
            ]
        )
    elif "Files" in ep and "Mailroom" not in ep:
        lines.extend(
            [
                "### sleek-website",
                "",
                "- `src/views/admin/files/index.js` — company-scoped file browser (select company, breadcrumbs, upload, new folder, search, standard folder structure). Webpack: `admin/files/index`.",
                "",
            ]
        )
    elif "Mailroom" in ep:
        lines.extend(
            [
                "### sleek-website",
                "",
                "- `src/views/admin/mailroom.js` — mailroom UI (shared patterns with Files; notify owner action). Webpack: `admin/mailroom`.",
                "",
            ]
        )
    elif "Request detail" in ep:
        lines.extend(
            [
                "### sleek-website",
                "",
                "- `src/views/admin/requests/edit.js` — request detail (document data, status, rich-text document, PDF, SleekSign). Webpack: `admin/requests/edit`.",
                "",
            ]
        )
    elif "Admin App > Requests" in ep:
        lines.extend(
            [
                "### sleek-website",
                "",
                "- `src/views/admin/requests/index.js` — request list; `requests/new.js` — new request. Webpack: `admin/requests/index`, `admin/requests/new`.",
                "",
            ]
        )
    elif "Documents" in ep and "Request Templates" not in ep:
        lines.extend(
            [
                "### sleek-website",
                "",
                "- `src/views/admin/documents.js` — document templates list and actions (create, generate, edit, delete). Webpack: `admin/documents`.",
                "",
            ]
        )
    elif "Request Templates" in ep:
        lines.extend(
            [
                "### sleek-website",
                "",
                "- `src/views/admin/request-templates.js` — request template CRUD. Webpack: `admin/request-templates`.",
                "",
            ]
        )
    elif "Auto-Sign" in ep:
        lines.extend(
            [
                "### sleek-website",
                "",
                "- `src/views/admin/auto-sign-configuration/index.js` — auto-sign employee table, add employees, toggles, column filters. Webpack: `admin/auto-sign-configuration`.",
                "",
            ]
        )
    elif "Camunda Workflows" in ep or "> Workflows" in ep:
        lines.extend(
            [
                "### sleek-website",
                "",
                "- `src/views/admin/sleek-workflow/` — Camunda task inbox and workflow UI (filter by process name). Also `src/views/admin/workflow/` for related legacy/new workflow entry.",
                "",
                "### sleek-workflow (Camunda)",
                "",
                "- Workflow definitions and instances are executed in **Camunda** (`sleek-workflow` repo per sheet); `sleek-back` integrates via workflow handlers and external tasks.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "### Codebase (indicative)",
                "",
                "- **Admin UI:** `sleek-website/src/views/admin/`; entries in `webpack/paths.js`.",
                "- **APIs:** `sleek-back` — `controllers/admin/`, `controllers/`, `controllers-v2/`; client `src/utils/api.js`.",
                "",
            ]
        )
        if deps and deps.strip():
            lines.append(f"- **Sheet dependencies:** {deps.strip()}")
            lines.append("")

    lines.extend(
        [
            "### Live app walkthrough",
            "",
            "- Confirms admin behaviour described in the master sheet for this capability.",
        ]
    )
    return "\n".join(lines)


def slugify(name: str) -> str:
    name = name.replace("–", "-").replace("—", "-").replace("&", "and")
    name = re.sub(r"[()]", "", name)
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def esc_table_cell(val: str) -> str:
    if val is None:
        return ""
    return str(val).replace("\n", " ").replace("|", "\\|")


def build_md(row: dict, feature_name: str) -> str:
    owner = row.get("Canonical Owner") or "TBD"
    deps = row.get("Dependencies / Related Flows") or "—"
    open_q = row.get("Open Questions") or ""
    reviewer = row.get("Reviewer") or ""

    lines = [
        f"# {feature_name}",
        "",
        "## Master sheet (draft)",
        "",
        "| Column | Value |",
        "|--------|-------|",
    ]
    fields = [
        ("Domain", row.get("Domain", "")),
        ("Feature Name", feature_name),
        ("Canonical Owner", owner),
        ("Primary User / Actor", row.get("Primary User / Actor", "")),
        ("Business Outcome", row.get("Business Outcome", "")),
        ("Entry Point / Surface", row.get("Entry Point / Surface", "")),
        ("Short Description", row.get("Short Description", "")),
        ("Variants / Markets", row.get("Variants / Markets", "")),
        ("Dependencies / Related Flows", deps if deps.strip() else "—"),
        ("Service / Repository", row.get("Service / Repository", "")),
        ("DB - Collections", row.get("DB - Collections", "")),
        ("Evidence Source", row.get("Evidence Source", "")),
        ("Criticality", row.get("Criticality", "")),
        ("Usage Confidence", row.get("Usage Confidence", "")),
        ("Disposition", row.get("Disposition", "")),
        ("Open Questions", open_q),
        ("Reviewer", reviewer),
        ("Review Status", row.get("Review Status", "")),
    ]
    for k, v in fields:
        lines.append(f"| **{k}** | {esc_table_cell(v)} |")
    lines.append("")
    lines.append("## Evidence")
    lines.append("")
    if feature_name in EVIDENCE_OVERRIDE:
        lines.append(EVIDENCE_OVERRIDE[feature_name])
        lines.append("")
        lines.append("### Live app walkthrough")
        lines.append("")
        lines.append("- Confirms admin UX described in the master sheet.")
    else:
        lines.append(
            evidence_from_entry_point(
                row.get("Entry Point / Surface", ""),
                feature_name,
                row.get("Dependencies / Related Flows", ""),
            )
        )
    lines.append("")
    return "\n".join(lines)


def is_admin_app_row(row: dict) -> bool:
    ep = (row.get("Entry Point / Surface") or "").strip()
    return ep.startswith("Admin App")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    skip_slug = "view-and-search-company-list"

    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Domain") != "Corpsec":
                continue
            if not is_admin_app_row(row):
                continue
            name = row["Feature Name"].strip()
            slug = slugify(name)
            if slug == skip_slug:
                continue
            path = OUT_DIR / f"{slug}.md"
            path.write_text(build_md(row, name), encoding="utf-8")
            print("wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
