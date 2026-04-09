# Generate Standard Folder Structure

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Generate Standard Folder Structure |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer |
| **Business Outcome** | Rapidly provision a consistent, regulation-appropriate folder layout for new companies without manual folder creation |
| **Entry Point / Surface** | Admin App > Files > Select Company > GENERATE STANDARD FOLDER STRUCTURE button |
| **Short Description** | Creates a predefined set of folders appropriate for the company's region. Template differs by market: HK creates 7 folders; UK creates 2 folders; AU creates 7 ASIC-aligned folders. SG folder set to be confirmed. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Confirm SG folder template contents and count. Confirm whether folder templates are configurable or hardcoded per region. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/files/index.js` — company-scoped file browser (select company, breadcrumbs, upload, new folder, search, standard folder structure). Webpack: `admin/files/index`.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.
