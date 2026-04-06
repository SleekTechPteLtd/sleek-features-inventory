# Download & Delete Company Files

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Download & Delete Company Files |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Retrieve or remove individual files from the company's document store |
| **Entry Point / Surface** | Admin App > Files > Select Company > file-level actions (download / delete) |
| **Short Description** | Download or delete individual files from the company's file store. Actions are available per file row. |
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
