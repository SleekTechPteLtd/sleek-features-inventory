# Edit Company Information & Business Activity Codes

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Edit Company Information & Business Activity Codes |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin User / Corpsec Officer |
| **Business Outcome** | Record business activity codes and address needed for ACRA filing and client profiling |
| **Entry Point / Surface** | Admin App > Company Overview > Overview tab – Company information section |
| **Short Description** | Business activity codes and address fields. Code system varies: SG uses SSIC (primary + secondary); UK uses SIC (4 fields); AU uses ANZIC (1 field); HK uses free-form activity description. Address structure is region-specific (SG: standard / HK: includes District + Address line 3 / UK: House Name/Number + Post Town + Postcode / AU: separate Registered + Business addresses + state-of-registration selector). SG also captures Web 3.0 / cryptocurrency declaration and Business Account projection fields. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | SG cryptocurrency / Web 3.0 questions — confirm whether these appear in any other region. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/company-overview/index.js` — primary revamped overview (tabs: Overview, People & Entities, Shares, Accounting, Deadlines, etc.).
- `src/views/admin/companies/edit/index.js` — legacy company edit (still linked from list when feature flags dictate).
- People & Entities partials under `src/views/admin/companies/edit/` (e.g. directors, shareholders, secretaries, registrable controllers, HK SCR, AU trust/public officer sections).

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
