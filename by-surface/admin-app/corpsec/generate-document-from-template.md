# Generate Document from Template

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Generate Document from Template |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Instantiate a document from an existing template for a specific company or request |
| **Entry Point / Surface** | Admin App > Documents > Generate action (per template row) |
| **Short Description** | Produces a document instance from a selected template. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Request Templates |
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
