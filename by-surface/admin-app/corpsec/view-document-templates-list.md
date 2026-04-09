# View Document Templates List

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | View Document Templates List |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Browse all available document templates for the region to identify what is available for use |
| **Entry Point / Surface** | Admin App > Documents |
| **Short Description** | Paginated list of document templates showing template name and actions. Content is region-specific. |
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

- `src/views/admin/documents.js` — document templates list and actions (create, generate, edit, delete). Webpack: `admin/documents`.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
