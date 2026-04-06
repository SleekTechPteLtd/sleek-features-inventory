# Manage Standard Users

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Manage Standard Users |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin User |
| **Business Outcome** | Grant and track standard portal access for non-admin company users |
| **Entry Point / Surface** | Admin App > Company Overview > People & Entities tab |
| **Short Description** | Section: Company's Standard Users with Add Standard User action. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** |  |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/company-overview/index.js` — primary revamped overview (tabs: Overview, People & Entities, Shares, Accounting, Deadlines, etc.).
- `src/views/admin/companies/edit/index.js` — legacy company edit (still linked from list when feature flags dictate).
- People & Entities partials under `src/views/admin/companies/edit/` (e.g. directors, shareholders, secretaries, registrable controllers, HK SCR, AU trust/public officer sections).

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
