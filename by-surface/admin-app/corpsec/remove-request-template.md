# Remove Request Template

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Remove Request Template |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Delete obsolete request templates to prevent staff from using outdated workflows |
| **Entry Point / Surface** | Admin App > Request Templates > Remove action (per template row) |
| **Short Description** | Remove a request template from the system. |
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

- `src/views/admin/request-templates.js` — request template CRUD. Webpack: `admin/request-templates`.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
