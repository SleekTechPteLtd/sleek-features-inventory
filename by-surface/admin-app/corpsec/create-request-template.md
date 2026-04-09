# Create Request Template

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Create Request Template |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Author a new request template to standardise and streamline corpsec service workflows |
| **Entry Point / Surface** | Admin App > Request Templates > NEW REQUEST TEMPLATE button |
| **Short Description** | Create a new request template specifying name, linked document template, and visibility setting (visible to clients or internal only). |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Document Templates |
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
