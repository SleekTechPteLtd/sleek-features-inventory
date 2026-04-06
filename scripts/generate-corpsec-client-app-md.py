#!/usr/bin/env python3
"""Generate corpsec/client-app/*.md from Corpsec CSV (Client App rows only)."""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "Corpsec - Sleek Feature Scope Audit Master Sheet - Sheet1.csv"
OUT_DIR = ROOT / "corpsec" / "client-app"

# Tailored evidence (repos: customer-main, customer-common, customer-root)
EVIDENCE: dict[str, str] = {
    "Client Portal – Company Secretary File Browser": """### customer-main

- Route `GET /customer/secretary` — `src/routes/routes.js` (`name: corporate-secretary`).
- `src/modules/corporate-secretary/containers/CorporateSecretary.vue` → `CorporateSecretaryPanel.vue` — folder tree, search, `FileDataTable` for files/folders (bulk actions, PDF flow per shared file explorer).

### customer-common

- `MasterLayout` / nav: `SleekDrawerContentV2.vue`, `SleekDrawer.vue`, `SleekMobileDrawer.vue` — `company_secretary` feature flag gates **Company secretary** left-nav entry.
- `src/modules/shared/components/presentational/FileDataTable.vue` — shared table/download copy used by secretary (and similar explorers).

### customer-root

- `src/root-config.js` — registers `@sleek/customer-main` for `activeWhen: ["/customer"]` (shell loads the MFE where `/customer/secretary` is handled).

### Live app walkthrough

- Confirms folder labels (A–H etc.), preview, search, and pagination described on the sheet.""",
    "Client Portal – On-going Requests View": """### customer-main

- Route `GET /customer/on-going-request` — `src/routes/routes.js` (`name: on-going-request`).
- `src/modules/customer-requests/containers/OnGoingRequest.vue` → `components/OnGoingRequestContent.vue` — active request cards/list.
- `src/proxies/back-end/customer-requests/get.js` — `GetCustomerRequestsListsProxy` (`TARGET_URL` `/customer-requests`).

### customer-common

- `MasterLayout` from `@sleek/customer-common` wraps the page; drawer exposes **Requests** → On-going when configured.

### customer-root

- `src/root-config.js` — `@sleek/customer-main` on `/customer`.

### Live app walkthrough

- Confirms latest / in-progress corpsec request presentation per audit notes.""",
    "Client Portal – History of Requests View": """### customer-main

- Route `GET /customer/history-of-request` — `src/routes/routes.js` (`name: history-of-request`).
- `src/modules/customer-requests/containers/HistoryOfRequest.vue` → `components/HistoryOfRequestContent.vue` — paginated completed requests table.
- `src/proxies/back-end/customer-requests/get.js` — list data via `/customer-requests`.

### customer-common

- Shared layout / navigation chrome for customer pages.

### customer-root

- `src/root-config.js` — MFE registration for `/customer`.

### Live app walkthrough

- Confirms columns (type, status, price, ID, date) and row paging.""",
    "Client Request – Change Company Name": """### customer-main

- Route `GET /customer/change-of-company-name` — `src/routes/routes.js`.
- `src/modules/change-of-company-name/containers/ChangeOfCompanyName.vue` (lazy chunk `customer-requests`) — end-user flow for name change / ACRA-related steps.

### customer-common

- `MasterLayout` and shared customer chrome.

### customer-root

- `src/root-config.js` — `/customer` → `customer-main`.

### Live app walkthrough

- Confirms catalogue entry under **Requests** and multi-step status progression on the sheet.""",
    "Client Request – Change Company Address": """### customer-main

- Route `GET /customer/change-of-address` — `src/routes/routes.js` (`ChangeOfAddress` container).
- Related automation path: `/customer/automation-workflow/...` (Camunda) for workflow-driven change-of-address in some flows.

### customer-common

- Layout / navigation.

### customer-root

- `src/root-config.js`.

### Live app walkthrough

- Confirms board resolution / signing / ACRA steps described on the sheet.""",
    "Client Request – Change of Director": """### customer-main

- Route `GET /customer/change-of-director-v2` — `src/routes/routes.js` (`ChangeOfDirectorContainerCamunda`).

### customer-common

- Shared workflow messaging (`MessagingTopic`, constants) used by Camunda-driven request UIs.

### customer-root

- `src/root-config.js`.

### Live app walkthrough

- Confirms nominee vs own-director branching and downstream signing/KYC notes.""",
    "Client Request – Resignation of Director": """### customer-main

- Route `GET /customer/resignation-of-director-v2` — `src/routes/routes.js` (`ResignationOfDirectorContainerCamunda`).

### customer-common

- Shared layout and workflow helpers as above.

### customer-root

- `src/root-config.js`.

### Live app walkthrough

- Confirms resignation + board resolution signing steps.""",
    "Client Request – Change of Business Activity": """### customer-main

- Route `GET /customer/change-of-business-activity` — `src/routes/routes.js` (`ChangeOfBizAct`).

### customer-common

- `MasterLayout`.

### customer-root

- `src/root-config.js`.

### Live app walkthrough

- Confirms SSIC / activity copy limits and free-flow steps.""",
    "Client Request – Open Bank Account": """### customer-main

- **Requests hub:** `src/modules/customer-requests/components/CustomerRequestContent.vue` — catalogue item `type == 'bank-account-opening'` (`BankWidgetIcon`), gated by `open_bank_account` app feature; uses `GetCompanyOpenBankAccountProxy` / `upsert` APIs.
- **Dashboard widget:** `src/modules/dashboard/components/DashboardBankAccountWidget.vue` with `proxies/back-end/company/get-open-bank-account.js` and `update-open-bank-account.js` (`/v2/company/:id/open-bank-account`, bank-account widget flags).

### customer-common

- Shared dashboard / layout where the widget may surface.

### customer-root

- `src/root-config.js`.

### Live app walkthrough

- Confirms bank picker, acknowledgements, and referral-style completion.""",
    "Client Request – Appointment of New Director": """### customer-main

- Route `GET /customer/appointment-of-director-v2` — `src/routes/routes.js` (`AppointmentOfDirectorContainerCamunda`).
- **Requests hub** lists `appoint-new-director` / `appointment-of-director` in `CustomerRequestContent.vue`.

### customer-common

- `MasterLayout`; workflow constants via `customer-sdk` / shared messaging.

### customer-root

- `src/root-config.js`.

### Live app walkthrough

- Confirms invitation + due diligence + ACRA filing narrative.""",
    "Client Request – Update My Details": """### customer-main

- **Requests hub:** `CustomerRequestContent.vue` — `UPDATE_MY_DETAILS` type (self-serve profile update messaging; links/actions to profile flow).
- **Profile:** `GET /customer/profile` — `src/routes/routes.js` (`user-profile`, `Profile` container) for personal particulars.

### customer-common

- `MasterLayout`.

### customer-root

- `src/root-config.js`.

### Live app walkthrough

- Confirms per-user profile update and ACRA reference copy.""",
    "Client Request – Change of Officer's Particulars": """### customer-main

- Route `GET /customer/change-of-particular` — `src/routes/routes.js` → `modules/change-of-particular/containers/ChangeOfParticular.vue` → `components/ChangeOfParticular*.vue` (document / address / upload steps driven by workflow messaging).
- **Requests hub:** `CustomerRequestContent.vue` maps `change-of-officer-particular` to the change-of-particulars icon/tile.

### customer-common

- `MessagingTopic` and workflow action constants consumed by the change-of-particular flow.

### customer-root

- `src/root-config.js`.

### Live app walkthrough

- Confirms director particulars change and ACRA filing path.""",
    "Client Request – Change of Shareholder's Particulars": """### customer-main

- Same **route** and module as officer particulars: `GET /customer/change-of-particular` — entry is distinguished by request catalogue type `change-of-shareholder-particular` in `CustomerRequestContent.vue`, which routes users into the shared change-of-particular workflow UI.

### customer-common

- Shared workflow messaging and layout as for officer particulars.

### customer-root

- `src/root-config.js`.

### Live app walkthrough

- Confirms shareholder-specific entry from **Requests** and shared downstream flow.""",
}


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
    svc = row.get("Service / Repository") or ""
    if not svc.strip():
        svc = "customer-main, customer-common, customer-root (client shell and shared UI)"

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
        ("Service / Repository", svc),
        ("DB - Collections", row.get("DB - Collections", "") or "—"),
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
    lines.append(EVIDENCE.get(feature_name, "### customer-main\n\n- Trace from `src/routes/routes.js` and `src/modules/` for this entry point.\n\n### Live app walkthrough\n\n- Confirms behaviour in the master sheet.\n"))
    lines.append("")
    return "\n".join(lines)


def is_client_app_row(row: dict) -> bool:
    ep = (row.get("Entry Point / Surface") or "").strip()
    return ep.startswith("Client App")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("Domain") != "Corpsec" or not is_client_app_row(row):
                continue
            name = row["Feature Name"].strip()
            path = OUT_DIR / f"{slugify(name)}.md"
            path.write_text(build_md(row, name), encoding="utf-8")
            print("wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
