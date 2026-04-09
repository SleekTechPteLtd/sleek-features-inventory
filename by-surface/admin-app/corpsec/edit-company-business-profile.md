# Edit Company Business Profile

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Edit Company Business Profile |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin User / Corpsec Officer |
| **Business Outcome** | Capture business-level attributes required for compliance and risk assessment |
| **Entry Point / Surface** | Admin App > Company Overview > Overview tab – About the company section |
| **Short Description** | Editable business-level attributes below the company header. Fields differ significantly by region. SG: Customer Risk Rating / SBA details / Business Account client / Preferred Incorporation date / Has Nominee Shareholder / Dormant flag. HK adds Language Preference (English / Traditional Chinese / Simplified Chinese) and Company Name 2 / 3 / Business Name / Has only one member since. UK adds Company Registered Email ID / EDD/CDD Complete Date / Target Date for Next EDD/CDD. AU has Business Name / Former Company Name / Dormant flag (no SBA / no Risk Rating shown). |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Customer Risk Rating absent from AU overview — confirm if it exists elsewhere in AU flow. EDD/CDD date fields are UK-only — verify. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/company-overview/index.js` — primary revamped overview (tabs: Overview, People & Entities, Shares, Accounting, Deadlines, etc.).
- `src/views/admin/companies/edit/index.js` — legacy company edit (still linked from list when feature flags dictate).
- People & Entities partials under `src/views/admin/companies/edit/` (e.g. directors, shareholders, secretaries, registrable controllers, HK SCR, AU trust/public officer sections).

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
