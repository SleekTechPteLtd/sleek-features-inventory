# Start Deadlines Workflow

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Start Deadlines Workflow |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer |
| **Business Outcome** | Trigger the structured compliance workflow for a financial year to drive timely filing |
| **Entry Point / Surface** | Admin App > Company Overview > Deadlines tab > START NOW button |
| **Short Description** | Initiates the structured deadlines compliance workflow for a selected FYE period via the START NOW button. SG-only; HK manages deadlines through direct date submission without a workflow trigger. UK and AU have no Deadlines tab. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Confirm SG-only status. Does the workflow trigger integrate with Camunda? |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/company-overview/index.js` — primary revamped overview (tabs: Overview, People & Entities, Shares, Accounting, Deadlines, etc.).
- `src/views/admin/companies/edit/index.js` — legacy company edit (still linked from list when feature flags dictate).
- People & Entities partials under `src/views/admin/companies/edit/` (e.g. directors, shareholders, secretaries, registrable controllers, HK SCR, AU trust/public officer sections).

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
