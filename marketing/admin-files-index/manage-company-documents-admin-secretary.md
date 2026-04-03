# Manage company documents (admin Secretary)

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage company documents (admin Secretary) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal operators (Sleek admin users with `profile === "admin"`); optional **Grant Permissions** UI gated to **IT Support** group membership (`SLEEK_GROUP_NAMES.IT_SUPPORT`). |
| **Business Outcome** | Staff can work in the correct client’s **Secretary** document tree so uploads, structure, and access stay aligned with expectations—keeping client-facing document storage usable and recoverable when folders are missing. |
| **Entry Point / Surface** | **sleek-website** admin: **Files** — `/admin/files/` (`AdminLayout`, sidebar `files`). Optional `?cid=` sets `company_id` in local storage; optional `?folder=` deep-links into a named folder under the current company then clears the query string. |
| **Short Description** | Operators choose a company (filterable select backed by admin company search), then browse the **Secretary** root under `/companies/{companyId}/` with breadcrumbs and back navigation. They can search files recursively by name, upload (picker or drag-drop for admins), download (zip or single encrypted file path), create folders, rename, move (including drag-drop onto folders and “Move to Parent”), delete (with optional multi-select when CMS `multi_file_delete` is enabled), preview in an overlay, and **Generate Folders** to call backend hydration of missing root folders. IT Support can open **Grant Permissions** to assign `can_view` / `can_edit` to a company user for the Secretary root or a selected file. |
| **Variants / Markets** | Company-scoped; **SG, HK, UK, AU** not encoded in these views — **Unknown** for market-specific behaviour. |
| **Dependencies / Related Flows** | **File service** (`getFileBaseUrl()`): `GET /files` (list, search `name` + `is_recursive`), `GET` paginated loads, `POST /files` upload, `POST /folders` create, `POST /files/{id}/move`, `POST /files/{id}/rename`, `DELETE /files/{ids}`, `POST /files/zip-and-download-files`, direct file URL for preview/download. **Main API** (`getBaseUrl()`): `POST /admin/companies/{companyId}/files/hydrate-root-folders`, `POST /admin/companies/{companyId}/files/permissions`; `GET` companies with `admin: true` for picker; `getCompanyUsers` for grant modal pagination. **Session/layout**: `viewUtil.fetchDashboardCommonData`, `AdminLayout`. **Related**: customer dashboard file explorer reuses `FileExplorerView` with `layoutType` other than `admin` (not this feature’s primary surface). Mailroom-only actions (e.g. **Notify Owner**) appear when `sidebarActiveMenuItemKey === "mailroom"` — not on admin Files. |
| **Service / Repository** | **sleek-website**: `src/views/admin/files/index.js`, `src/views/file-explorer.js`, `src/views/files/grant-permissions-modal.js`, `src/utils/api.js` (file + admin company endpoints), `src/utils/view.js` (upload helpers). **File microservice** and **sleek-back** (admin hydrate/permissions, persistence): not in this repo. |
| **DB - Collections** | **MongoDB** (or other stores) for files, folders, and permissions — **Unknown** from sleek-website; persistence lives behind file and admin APIs. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact RBAC matrix for admin file actions vs `user.permissions.files` / `companies` (Generate Folders disable logic) vs backend enforcement. Whether `lost` / `recovered` file flags are still active in production file models. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/files/index.js`

- Mounts `FileExplorerView` with `sidebarActiveMenuItemKey="files"`, `layoutType="admin"`, `rootFolderName="Secretary"`, `sortFilesBy={["name"]}`, `sortFilesOrder={[1]}`, `companiesSelectIsVisible={true}`.

### `src/views/file-explorer.js` (`FileExplorerView`)

- **Layout**: `layoutType === "admin"` → `AdminLayout`; else `DashboardLayout`.
- **Company selection**: When `companiesSelectIsVisible`, shows Blueprint `Select` over `companiesList` from `api.getCompanies({ query: { name }, admin: true })` as the user types (`handleSearchCompany`).
- **Root folder**: `fetchRootFolder` → `api.getAllFiles` with `local_path: /companies/{selectedCompanyId}/`, `name: rootFolderName` (default **Secretary**); uses last match.
- **Listing**: `fetchFiles` → `api.getFiles` with `local_path`, `sort_by`, `sort_order`; pages in chunks of 20 until `count` satisfied.
- **Search**: `handleChangeSearchFiles` passes `query` with `name`, `is_recursive: true` when keyword non-empty.
- **Admin toolbar**: New folder (`api.createFolder` → `POST .../folders`), upload (`viewUtil.uploadFile` → file API), delete (`api.deleteFile`), download (`api.zipAndDownloadFiles` or single `encrypted_s3` via direct URL), **Generate Folders** (`api.hydrateCompanyFolders` → `POST /admin/companies/{id}/files/hydrate-root-folders`), **Grant Permissions** if `hasGrantPermission` from `api.isMember({ group_name: IT_SUPPORT })`.
- **Grant**: `handleClickGrantPermissions` → dialog with `GrantPermissionsModalContent`; `api.grantPermissions(companyId)` with `user_id`, `permissions[]`, and either `selected_file` or `folder` (root folder name).
- **Organize**: `interactjs` drag from file to folder → `api.moveFile`; context menu **Move to Parent** → `moveFile` with parent from breadcrumbs.
- **Other**: `redirectToFolder` for `?folder=` query; filters out `lost && !recovered` from display; optional mailroom notify when `sidebarActiveMenuItemKey == "mailroom"`.

### `src/views/files/grant-permissions-modal.js` (`GrantPermissionsModalContent`)

- Loads all company users via `getCompanyUsers(companyId)` with pagination (`limit: 20`, `include_pagination_metadata: true`, `lean: true`); dedupes by `user._id`.
- Checkboxes for **View** (`can_view`) and **Edit** (`can_edit`); selected user from `<select>`.

### `src/utils/api.js` (selected)

- **Files**: `getFiles` → `GET ${getFileBaseUrl()}/files`; `createFolder` → `POST .../folders`; `moveFile` → `POST .../files/{id}/move`; `renameFile` → `POST .../files/{id}/rename`; `deleteFile` → `DELETE .../files/{fileId}`; `zipAndDownloadFiles` → `POST .../files/zip-and-download-files`.
- **Admin**: `hydrateCompanyFolders` → `POST ${getBaseUrl()}/admin/companies/{companyId}/files/hydrate-root-folders`; `grantPermissions` → `POST ${getBaseUrl()}/admin/companies/{companyId}/files/permissions`.

### Navigation

- `src/components/new-admin-side-menu.js` / `admin-side-menu.js`: **Files** → `href="/admin/files/"`.
