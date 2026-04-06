# View & Edit Staff Assigned to Company

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | View & Edit Staff Assigned to Company |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin User / Team Lead |
| **Business Outcome** | Ensure accountability by linking named staff to each client company across all service lines |
| **Entry Point / Surface** | Admin App > Company Overview > Overview tab – Staff assigned panel (view) / Accounting tab – Edit assignee (edit) |
| **Short Description** | View and assign named staff members to the company across all service lines. Role set differs by region. SG: ~25 roles incl. Named CS / CS Team Lead / Immigration / Portfolio Lead / Customer Champion. HK: ~20 roles incl. Auditor / Auditor Backup. UK/AU: ~14 roles incl. Senior Accountant / Junior Accountant / CSS In Charge / Tax and Payroll Manager. All regions editable via 'Edit assignee' action. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Immigration-related roles appear only in SG — confirm. Auditor roles appear only in HK — confirm. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/company-overview/index.js` — primary revamped overview (tabs: Overview, People & Entities, Shares, Accounting, Deadlines, etc.).
- `src/views/admin/companies/edit/index.js` — legacy company edit (still linked from list when feature flags dictate).
- People & Entities partials under `src/views/admin/companies/edit/` (e.g. directors, shareholders, secretaries, registrable controllers, HK SCR, AU trust/public officer sections).

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
