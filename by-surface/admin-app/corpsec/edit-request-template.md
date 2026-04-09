# Edit Request Template

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Edit Request Template |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Update an existing request template to keep workflows aligned with current requirements |
| **Entry Point / Surface** | Admin App > Request Templates > Edit action (per template row) |
| **Short Description** | Modify the name, document template link, or visibility setting of an existing request template. |
| **Variants / Markets** | SG, HK, UK, AU |
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

- `src/views/admin/request-templates.js` — request template CRUD. Webpack: `admin/request-templates`.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
