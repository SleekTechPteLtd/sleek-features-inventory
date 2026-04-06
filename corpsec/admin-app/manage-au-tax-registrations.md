# Manage AU Tax Registrations

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Manage AU Tax Registrations |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Record and track the company's Australian tax registration elections (ABN, GST, PAYGW, FBT) to support compliance and onboarding |
| **Entry Point / Surface** | Admin App > Company Overview > Tax tab (AU only) |
| **Short Description** | AU-only tab. Four registration sections: ABN Registration (first-time in Australia flag) / Goods & Services Tax (GST) / Pay As You Go Withholding (PAYGW) / Fringe Benefit Tax (FBT). Each is a Yes/No toggle capturing the client's registration preference. |
| **Variants / Markets** | AU |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Confirm whether registration elections trigger downstream workflows or are record-only. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/company-overview/index.js` — primary revamped overview (tabs: Overview, People & Entities, Shares, Accounting, Deadlines, etc.).
- `src/views/admin/companies/edit/index.js` — legacy company edit (still linked from list when feature flags dictate).
- People & Entities partials under `src/views/admin/companies/edit/` (e.g. directors, shareholders, secretaries, registrable controllers, HK SCR, AU trust/public officer sections).

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
