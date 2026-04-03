# Bulk import companies from CSV

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Bulk import companies from CSV |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations / support staff (Admin) |
| **Business Outcome** | Operators can seed or reconcile many customer-support custom company records in one step using a standard CSV, instead of creating or editing them one by one. |
| **Entry Point / Surface** | Sleek Admin > Customer Support (`/admin/customer-support/`) — toolbar actions **Download Template** and **Bulk Upload** above the company list. |
| **Short Description** | **Download Template** fetches a CSV template from the Staff Allocation API and saves it via the browser. **Bulk Upload** opens a file picker (CSV only), posts the file to the API, and shows how many rows were inserted vs updated and any row-level errors. Confirming the success dialog refreshes the custom company table. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `StaffAllocationAPI` → resource-allocator (`POST /companies/bulk`, `GET /companies/bulk/template`); list refresh via `CustomCompanyTable.refreshTable` after upload; complements single-row **Create Company** on the same page. |
| **Service / Repository** | sleek-website; resource-allocator (Staff Allocation API backend, not in this repo) |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | MongoDB collections and CSV column contract are owned by resource-allocator and are not defined in sleek-website. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Page**: Webpack entry `admin/customer-support` → `src/views/admin/customer-support/index.js` — `CustomerSupportView` with `AdminLayout` (`sidebarActiveMenuItemKey="customer-support"`, `hideDrawer={true}`), primary toolbar title “Customer Support”.
- **Download template**: `useDownloadTemplate` in `src/views/admin/customer-support/hooks/download-template.js` — `StaffAllocationAPI.instance.downloadBulkUploadTemplate()` → `GET /companies/bulk/template` (`src/utils/api-staff-allocation.js`). Builds a `Blob` from `response.data` and `Content-Type`, derives filename from `Content-Disposition` or defaults to `template.csv`, triggers download (with `msSaveOrOpenBlob` fallback for older IE). Errors parsed with `errorParser` from `src/views/admin/customer-support/utils.js`.
- **Bulk upload**: `useBulkUpload` in `src/views/admin/customer-support/hooks/bulk-upload.js` — hidden `<input type="file" accept=".csv,application/csv,text/csv">`, on change `StaffAllocationAPI.instance.bulkUpload(formData)` with `FormData` field `file` → `POST /companies/bulk` (`bulkUpload` in `api-staff-allocation.js`). Response shape per JSDoc `BulkUploadResponseData`: `inserted`, `updated`, `errors` (array of strings). Success shows Blueprint `Alert` with totals and per-row error lines; `onConfirm` calls `refreshTable()` which invokes `tableRef.current.refreshTable()` on `CustomCompanyTable` and `resetUploadStatus()`.
- **UI wiring**: `index.js` — buttons “Bulk Upload” (`bulkUpload`, `isUploading`) and “Download Template” (`downloadTemplate`, `isDownloading`); error alerts for download and upload failures.
- **API client**: `StaffAllocationAPI` — axios base URL from `API_STAFF_ALLOCATION_URL`, else production `https://resource-allocator.sleek.sg` or dev `http://localhost:3015`; JSON responses unwrapped via interceptor `{ data }` from `response.data` when `response.data` is a plain object (`src/utils/api-staff-allocation.js`).
