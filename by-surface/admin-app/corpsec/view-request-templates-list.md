# View Request Templates List

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | View Request Templates List |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Browse all configured request templates for the region to understand available corpsec workflows |
| **Entry Point / Surface** | Admin App > Request Templates |
| **Short Description** | Paginated list of request templates showing Name, Document Template, Visible flag (Yes/No), and Created At. Content is region-specific: SG has ~215 templates, HK has ~139 (including Chinese-language entries), UK has 11, AU has 4. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | HK templates include Chinese-language names — confirm whether language is user-selectable or template-driven. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/request-templates.js` — request template CRUD. Webpack: `admin/request-templates`.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
