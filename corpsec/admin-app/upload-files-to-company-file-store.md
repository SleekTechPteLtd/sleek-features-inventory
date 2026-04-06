# Upload Files to Company File Store

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Upload Files to Company File Store |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Store client documents centrally within the company's file store for easy access and retrieval |
| **Entry Point / Surface** | Admin App > Files > Select Company > UPLOAD button |
| **Short Description** | Upload one or more files to the currently selected folder in the company's file store. |
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
