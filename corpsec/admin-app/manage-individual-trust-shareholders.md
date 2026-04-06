# Manage Individual Trust Shareholders

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Manage Individual Trust Shareholders |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer |
| **Business Outcome** | Record individual beneficiaries holding shares via a trust structure, as required under Australian corporate law |
| **Entry Point / Surface** | Admin App > Company Overview > People & Entities tab – Individual Trust Shareholders section |
| **Short Description** | AU-only entity type. Add and manage individual trust shareholders. Supports AU trust structures not applicable in SG, HK, or UK. |
| **Variants / Markets** | AU |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
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
