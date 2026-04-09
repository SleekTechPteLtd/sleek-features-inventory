# Manage Registrable Controllers

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Manage Registrable Controllers |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Compliance Officer / Corpsec Officer |
| **Business Outcome** | Fulfil the statutory obligation to record persons with significant control over the company |
| **Entry Point / Surface** | Admin App > Company Overview > People & Entities tab |
| **Short Description** | Add and manage persons with significant control (Registrable Controllers) as required by Singapore company law. This section is SG-only. HK has a structurally different equivalent: Significant Controllers Register + Designated Representatives (separate feature rows). |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Confirm HK Significant Controllers Register is the statutory equivalent of SG Registrable Controllers. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/company-overview/index.js` — primary revamped overview (tabs: Overview, People & Entities, Shares, Accounting, Deadlines, etc.).
- `src/views/admin/companies/edit/index.js` — legacy company edit (still linked from list when feature flags dictate).
- People & Entities partials under `src/views/admin/companies/edit/` (e.g. directors, shareholders, secretaries, registrable controllers, HK SCR, AU trust/public officer sections).

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
