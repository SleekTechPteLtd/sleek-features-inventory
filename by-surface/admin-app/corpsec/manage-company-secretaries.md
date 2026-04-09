# Manage Company Secretaries

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Manage Company Secretaries |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer |
| **Business Outcome** | Record the appointed company secretary to satisfy statutory requirements |
| **Entry Point / Surface** | Admin App > Company Overview > People & Entities tab |
| **Short Description** | Add and manage company secretaries. SG and HK offer two actions: Add Company Secretary (external) and Add Sleek Secretary (Sleek-appointed). UK offers Add Company Secretary only. AU has no Company Secretaries section in People & Entities. |
| **Variants / Markets** | SG, HK, UK |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Confirm AU has no secretary requirement or if it is tracked elsewhere. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/company-overview/index.js` — primary revamped overview (tabs: Overview, People & Entities, Shares, Accounting, Deadlines, etc.).
- `src/views/admin/companies/edit/index.js` — legacy company edit (still linked from list when feature flags dictate).
- People & Entities partials under `src/views/admin/companies/edit/` (e.g. directors, shareholders, secretaries, registrable controllers, HK SCR, AU trust/public officer sections).

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
