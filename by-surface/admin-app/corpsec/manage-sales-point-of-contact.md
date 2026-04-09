# Manage Sales Point of Contact

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Manage Sales Point of Contact |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin User / Sales |
| **Business Outcome** | Capture the client-side sales contact for a UK company to support account management and renewals |
| **Entry Point / Surface** | Admin App > Company Overview > People & Entities tab – Sales point of contact section |
| **Short Description** | UK-only section at the bottom of People & Entities. Records the Name, Email, and Phone of the company's sales point of contact. |
| **Variants / Markets** | UK |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | Low |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Confirm whether this field is used operationally or for CRM purposes only. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/company-overview/index.js` — primary revamped overview (tabs: Overview, People & Entities, Shares, Accounting, Deadlines, etc.).
- `src/views/admin/companies/edit/index.js` — legacy company edit (still linked from list when feature flags dictate).
- People & Entities partials under `src/views/admin/companies/edit/` (e.g. directors, shareholders, secretaries, registrable controllers, HK SCR, AU trust/public officer sections).

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
