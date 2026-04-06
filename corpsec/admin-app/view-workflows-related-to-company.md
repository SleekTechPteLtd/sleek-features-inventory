# View Workflows Related to Company

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | View Workflows Related to Company |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin User / Corpsec Officer |
| **Business Outcome** | Give admins quick visibility of any active or completed workflows linked to a specific company without leaving the company overview |
| **Entry Point / Surface** | Admin App > Company Overview > Overview tab – Workflows related to the company section |
| **Short Description** | Inline section at the bottom of the Overview tab listing all workflows associated with the company (e.g. Accounting Onboarding V2) with their status (IN PROGRESS / DONE) and a view link. Present in all four regions. |
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
