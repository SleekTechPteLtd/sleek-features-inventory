# View CDD Questionnaire History

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | View CDD Questionnaire History |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Compliance Officer / Admin User |
| **Business Outcome** | Track Customer Due Diligence refresh events and know whether the CDD questionnaire is complete |
| **Entry Point / Surface** | Admin App > Company Overview > Company Info tab |
| **Short Description** | Company Info tab (SG-only) shows chronological CDD refresh events with date and questionnaire completion status. Tab is not present in HK, UK, or AU admin. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Confirm whether HK, UK, AU have an equivalent CDD history view accessible elsewhere in their admin flows. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/company-overview/index.js` — primary revamped overview (tabs: Overview, People & Entities, Shares, Accounting, Deadlines, etc.).
- `src/views/admin/companies/edit/index.js` — legacy company edit (still linked from list when feature flags dictate).
- People & Entities partials under `src/views/admin/companies/edit/` (e.g. directors, shareholders, secretaries, registrable controllers, HK SCR, AU trust/public officer sections).

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
