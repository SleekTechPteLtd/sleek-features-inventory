# Create Folder in Company File Store

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Create Folder in Company File Store |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Organise company documents into a structured folder hierarchy for efficient retrieval |
| **Entry Point / Surface** | Admin App > Files > Select Company > NEW FOLDER button |
| **Short Description** | Create a new folder within the currently selected path in the company's file store. |
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

- `src/views/admin/files/index.js` — company-scoped file browser (select company, breadcrumbs, upload, new folder, search, standard folder structure). Webpack: `admin/files/index`.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
