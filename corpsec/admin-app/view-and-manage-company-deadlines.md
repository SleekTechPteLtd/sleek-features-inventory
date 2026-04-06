# View & Manage Company Deadlines

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | View & Manage Company Deadlines |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Track regulatory filing deadlines per financial year to ensure timely compliance |
| **Entry Point / Surface** | Admin App > Company Overview > Deadlines tab |
| **Short Description** | Track regulatory filing deadlines for a company. Structure differs by region. SG: FYE-based table listing deadlines with Name / Regulatory Due Date / Completed On / Filing Done columns, plus subscription panel. HK: AGM-focused layout with fields for Deadline to hold AGM / Extended Deadline / Date AGM held / Deadline to file Annual Return / Extended Deadline / Date Annual Return Filed — all editable with direct date submission. Deadlines tab is absent in UK and AU. |
| **Variants / Markets** | SG, HK |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | HK deadline management is direct date entry rather than a workflow trigger — confirm whether the HK flow integrates with any downstream workflow. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/company-overview/index.js` — primary revamped overview (tabs: Overview, People & Entities, Shares, Accounting, Deadlines, etc.).
- `src/views/admin/companies/edit/index.js` — legacy company edit (still linked from list when feature flags dictate).
- People & Entities partials under `src/views/admin/companies/edit/` (e.g. directors, shareholders, secretaries, registrable controllers, HK SCR, AU trust/public officer sections).

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
