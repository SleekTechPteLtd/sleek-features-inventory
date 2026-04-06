# Edit Document Template

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Edit Document Template |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Maintain and update existing document templates to keep them current and accurate |
| **Entry Point / Surface** | Admin App > Documents > Edit action (per template row) |
| **Short Description** | Edit the content and metadata of an existing document template. |
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
