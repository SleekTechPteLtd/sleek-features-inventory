# View & Edit Company Core Details

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | View & Edit Company Core Details |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin User / Corpsec Officer |
| **Business Outcome** | Keep the company's master record accurate throughout its lifecycle |
| **Entry Point / Surface** | Admin App > Company Overview > Overview tab – EDIT PAGE |
| **Short Description** | Editable company header fields and status. Field set varies by region: SG has UEN / ACRA filing dates; HK has CR No. + BR No. + Last Filing Date + Financial Year End + Xero Contact ID; UK has Company Number + Tax Reference (UTR) + Companies House Authentication Code + Xero Contact ID; AU has ABN + ACN + Tax File Number + Entity Type (replaces Company Type). All regions show UPDATE and DELETE (Draft only) actions. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | DELETE rule (Draft only) – verify across all regions. Xero Contact ID present in HK and UK but not SG/AU – confirm. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/company-overview/index.js` — primary revamped overview (tabs: Overview, People & Entities, Shares, Accounting, Deadlines, etc.).
- `src/views/admin/companies/edit/index.js` — legacy company edit (still linked from list when feature flags dictate).
- People & Entities partials under `src/views/admin/companies/edit/` (e.g. directors, shareholders, secretaries, registrable controllers, HK SCR, AU trust/public officer sections).

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
