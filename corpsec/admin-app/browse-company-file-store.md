# Browse Company File Store

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Browse Company File Store |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Give staff direct access to all documents stored under a company without leaving the admin app |
| **Entry Point / Surface** | Admin App > Files > Select Company |
| **Short Description** | Company-scoped file browser. Admin selects a company via dropdown to view its folder/file hierarchy. Supports folder navigation with breadcrumb path. Requires company selection before any files are shown. |
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

- `src/views/admin/files/index.js` — company-scoped file browser (select company, breadcrumbs, upload, new folder, search, standard folder structure). Webpack: `admin/files/index`.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
