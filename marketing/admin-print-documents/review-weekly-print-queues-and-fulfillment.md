# Review weekly print queues and record fulfillment

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Review weekly print queues and record fulfillment |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal **Admin** operators (Sleek admin users with `user.profile === "admin"`). The **Print Documents** nav item is shown only when **`printservice.enabled`** is true in admin menu config. |
| **Business Outcome** | Operations can work through **week-bucketed** print work (company documents and address labels), pull the right **encrypted** files for physical printing, and **mark request instances as printed** so fulfillment status matches reality before **time-bucketed cleanup** (UI copy: items cleared after about five weeks). |
| **Entry Point / Surface** | **sleek-website** admin: **Print Documents** — `/admin/print-documents/` (`AdminLayout`, sidebar key `print-documents`). Menu entry **Print Documents** appears under the print-service block when enabled. |
| **Short Description** | Staff see up to **six weekly folders** (named `Printing_WC-{DDMMMYY}`), each containing **Company Docs** and **Address Label** subfolders. Opening a subfolder loads **request instances** for that week range and folder type from the main API. Staff **multi-select** rows, **download** selected files as a **zip** of encrypted S3 objects via the file service, and **mark selected as printed** so backend status updates to `PRINTED`. Week-level and subfolder-level **print-complete** indicators use `folder-print-status` (`has_printed_all_documents`). |
| **Variants / Markets** | Not encoded in these views — **Unknown** for SG/HK/UK/AU-specific rules. |
| **Dependencies / Related Flows** | **Main API** (`getBaseUrl()`): `GET /admin/request-instances/printing-service` (query: `start_of_week`, `end_of_week`, `folder_type` `COMPANY_DOCS` \| `ADDRESS_LABEL`); `GET .../printing-service/folder-print-status` (same query + `folder_type` for aggregate print status); `POST .../printing-service/mark-as-printed` (body: `fileIds`). **File service** (`getFileBaseUrl()`): `POST /files/zip-and-download-files` with `fileIds`, `fileType: "encrypted_s3"`, `baseFileName`. **Session/layout**: `viewUtil.fetchDashboardCommonData`, `AdminLayout`. **Related**: client request-instance and document flows upstream of printing; physical print and warehouse ops downstream. |
| **Service / Repository** | **sleek-website**: `src/views/admin/print-documents/index.js`, `components/folder-explorer.js`, `components/documents-list.js`, `components/documents.js`, `src/utils/api.js`. **sleek-back** (or equivalent) for admin printing-service routes and persistence — not in this repo. |
| **DB - Collections** | **Unknown** from sleek-website; request instances and file metadata live behind main API and file service. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Where **`printservice.enabled`** is sourced and who can enable it. Exact backend retention/cleanup job for print-queue artifacts vs the on-screen “5 weeks” message. Whether `getRequestInstancesPrintingService` response shape is always an array (folder-explorer assigns `files: requestInstanceResponse.data`). `documents-list.js` download handler references `this` inside a function component (likely dead / buggy paths). Search filters `filteredResults` in place and can shrink the list irreversibly until cleared — intentional? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/print-documents/index.js`

- Renders `FolderExplorerView` with `sidebarActiveMenuItemKey="print-documents"`, `layoutType="admin"`, `rootFolderName="root"`, `sortFilesBy={["createdAt"]}`, `sortFilesOrder={[-1]}`, `companiesSelectIsVisible={false}` (no company picker — global print queue).

### `src/views/admin/print-documents/components/folder-explorer.js` (`FolderExplorerView`)

- **Layout**: `layoutType === "admin"` → `AdminLayout`.
- **Auth gate**: `fetchFolders` only if `user.profile === "admin"`.
- **Week buckets**: `fetchFolders` builds six synthetic **folder** entries; for each week `i` (0..5) calls `getRequestInstancesPrintingServiceNotPrinted` twice with `folder_type: "COMPANY_DOCS"` and `"ADDRESS_LABEL"` and `start_of_week` / `end_of_week` from `moment` week boundaries. Subfolders carry `folder_type`, week range ISO strings, and `is_printed` from `data.has_printed_all_documents`.
- **Navigation**: Double-click **folder** → `fetchSubFolders` (shows two subfolders). Double-click **sub_folder** → `openFolder` → `getRequestInstancesPrintingService` with week + `folder_type`, then `selectedFolderType: "encrypted_s3"` and `files` from response `data`.
- **UI copy**: “Print documents in these folders. They will be cleared once they are 5 weeks old. Individual files will still be stored in respective companies.”
- **Icons**: Green print icon when week folder has all subfolders printed, or when document subfolder `is_printed`; row selection via Blueprint `Checkbox`.

### `src/views/admin/print-documents/components/documents-list.js` (`DocumentsListView`)

- **Download**: `zipAndDownloadFiles` with `fileIds` (from row selection by `client_provided_document`), `fileType: "encrypted_s3"`, `baseFileName: `${rootFolder.name}-${currentFolder.name}``; blob saved as `{rootFolder.name}-{YYYYMMDD}.zip`.
- **Mark printed**: `markRequestInstancesAsPrinted` with `fileIds` from selected **request instance** ids (`selectedReqInstance`); optimistic local update sets `printing_service_status = "PRINTED"` on matching rows.
- **Search**: Filters by `document_name` (string values joined); mutates `filteredResults` state (see open questions).

### `src/views/admin/print-documents/components/documents.js` (`DocsList`)

- Sortable table (`useSortableData`): **Name**, **Print Status** (green confirm icon vs hollow circle for not printed).
- Selection maps checkbox to both `client_provided_document` (for zip file id list) and `_id` (for mark-as-printed), and supports select-all.

### `src/utils/api.js`

- `getRequestInstancesPrintingService` → `GET ${getBaseUrl()}/admin/request-instances/printing-service`
- `getRequestInstancesPrintingServiceNotPrinted` → `GET ${getBaseUrl()}/admin/request-instances/printing-service/folder-print-status`
- `markRequestInstancesAsPrinted` → `POST ${getBaseUrl()}/admin/request-instances/printing-service/mark-as-printed`
- `zipAndDownloadFiles` → `POST ${getFileBaseUrl()}/files/zip-and-download-files`

### Navigation

- `src/components/new-admin-side-menu.js`: **Print Documents** → `href="/admin/print-documents/"`, `selected` when `activeMenuItemKey === "print-documents"`, wrapped in `printservice.enabled` conditional.
