# Manage Significant Controllers Register

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Manage Significant Controllers Register |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer |
| **Business Outcome** | Fulfil HK statutory obligation to identify and record persons with significant control over the company |
| **Entry Point / Surface** | Admin App > Company Overview > People & Entities tab – Significant Controllers Register section |
| **Short Description** | HK-specific section replacing SG's Registrable Controllers. Add and manage Significant Controllers as required by the Companies Ordinance (Cap. 622). Records name and relevant details of each controller. |
| **Variants / Markets** | HK |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Confirm this is the direct statutory equivalent of SG Registrable Controllers. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/company-overview/index.js` — primary revamped overview (tabs: Overview, People & Entities, Shares, Accounting, Deadlines, etc.).
- `src/views/admin/companies/edit/index.js` — legacy company edit (still linked from list when feature flags dictate).
- People & Entities partials under `src/views/admin/companies/edit/` (e.g. directors, shareholders, secretaries, registrable controllers, HK SCR, AU trust/public officer sections).

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
