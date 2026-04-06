# Manage Ultimate Beneficial Owners (UBOs)

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Manage Ultimate Beneficial Owners (UBOs) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Compliance Officer / Corpsec Officer |
| **Business Outcome** | Record ultimate beneficial owners for AML and KYC purposes |
| **Entry Point / Surface** | Admin App > Company Overview > People & Entities tab |
| **Short Description** | Section: Company's Ultimate Beneficial Owners with Add UBO action. |
| **Variants / Markets** | SG, HK |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | UBO section absent in UK and AU admin — confirm whether UBO data is captured in those regions via a different mechanism. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/company-overview/index.js` — primary revamped overview (tabs: Overview, People & Entities, Shares, Accounting, Deadlines, etc.).
- `src/views/admin/companies/edit/index.js` — legacy company edit (still linked from list when feature flags dictate).
- People & Entities partials under `src/views/admin/companies/edit/` (e.g. directors, shareholders, secretaries, registrable controllers, HK SCR, AU trust/public officer sections).

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
