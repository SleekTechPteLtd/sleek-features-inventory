# Delete Document Template

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Delete Document Template |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Remove obsolete or incorrect document templates to keep the template library clean |
| **Entry Point / Surface** | Admin App > Documents > Delete action (per template row) |
| **Short Description** | Delete an existing document template from the system. |
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

- `src/views/admin/documents.js` — document templates list and actions (create, generate, edit, delete). Webpack: `admin/documents`.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
