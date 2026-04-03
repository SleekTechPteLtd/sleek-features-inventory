# Manage client accounting files in admin

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage client accounting files in admin |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal operators (Sleek admin users with `profile === "admin"`); optional **Grant Permissions** UI gated to **IT Support** group membership (`SLEEK_GROUP_NAMES.IT_SUPPORT`). |
| **Business Outcome** | Operators work in the correct client’s **Accounting** document tree so bookkeeping-related files can be browsed, uploaded, organized, and permissioned—keeping accounting artifacts available for service and bookkeeping. |
| **Entry Point / Surface** | **sleek-website** admin: **Accounting** (under the expandable **Files** group when `accounting` menu feature is enabled) — `/admin/accounting/` (`AdminLayout`). Optional `?cid=` sets `company_id` in local storage; optional `?folder=` deep-links into a named folder under the current company then clears the query string. |
| **Short Description** | Same **FileExplorerView** behaviour as admin **Files (Secretary)** but rooted at the **Accounting** folder under `/companies/{companyId}/`: company filterable select (`api.getCompanies` with `admin: true`), browse with breadcrumbs, recursive name search, upload (picker or drag-drop for admins), download (zip or single `encrypted_s3`), new folder, rename, move (drag-drop and **Move to Parent**), delete (multi-select when CMS `multi_file_delete` is enabled), preview overlay, **Generate Folders** (`hydrateCompanyFolders`), and **Grant Permissions** for IT Support (root folder or selected file). |
| **Variants / Markets** | Company-scoped; **SG, HK, UK, AU** not encoded in these views — **Unknown** for market-specific behaviour. |
| **Dependencies / Related Flows** | **File service** (`getFileBaseUrl()`): `GET /files` (list, search with `name` + `is_recursive`), paginated loads, `POST` upload, `POST /folders`, `POST /files/{id}/move`, `POST /files/{id}/rename`, `DELETE /files/{ids}`, `POST /files/zip-and-download-files`, direct file URL for preview/download. **Main API** (`getBaseUrl()`): `POST /admin/companies/{companyId}/files/hydrate-root-folders`, `POST /admin/companies/{companyId}/files/permissions`; admin company search for picker; company users for grant modal. **Session/layout**: `viewUtil.fetchDashboardCommonData`, `AdminLayout`. **Related**: `src/views/admin/files/index.js` — same component with `rootFolderName="Secretary"`. Mailroom-only toolbar/context actions require `sidebarActiveMenuItemKey === "mailroom"` — not used on this entry. |
| **Service / Repository** | **sleek-website**: `src/views/admin/accounting/index.js`, `src/views/file-explorer.js`, `src/views/files/grant-permissions-modal.js`, `src/utils/api.js`, `src/utils/view.js`. **File microservice** and **sleek-back** (hydrate/permissions, persistence): not in this repo. |
| **DB - Collections** | **MongoDB** (or other stores) for files, folders, and permissions — **Unknown** from sleek-website; persistence lives behind file and admin APIs. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `sidebarActiveMenuItemKey="files"` on the Accounting entry may not match the **Accounting** nav highlight (`activeMenuItemKey === "accounting"` in `new-admin-side-menu.js`) — verify intended UX. Exact RBAC matrix for admin file actions vs `user.permissions.files` / `companies` (Generate Folders disable logic) vs backend enforcement. Whether `lost` / `recovered` file flags are still active in production file models. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/accounting/index.js`

- Mounts `FileExplorerView` with `sidebarActiveMenuItemKey="files"`, `layoutType="admin"`, `rootFolderName="Accounting"`, `sortFilesBy={["name"]}`, `sortFilesOrder={[1]}`, `companiesSelectIsVisible={true}`.

### `src/views/file-explorer.js` (`FileExplorerView`)

Shared implementation; **Accounting** vs **Secretary** differs only by `rootFolderName` from the entry `index.js`.

- **Layout**: `layoutType === "admin"` → `AdminLayout`.
- **Company selection**: When `companiesSelectIsVisible`, Blueprint `Select` + `api.getCompanies({ query: { name }, admin: true })` (`handleSearchCompany` / `fetchCompaniesList`).
- **Root folder**: `fetchRootFolder` → `api.getAllFiles` with `local_path: /companies/{selectedCompanyId}/`, `name: this.props.rootFolderName` — here **Accounting** (`last(files)`).
- **Listing**: `fetchFiles` → `api.getFiles` with `local_path`, `sort_by`, `sort_order`; loads in chunks of 20 until `count` satisfied.
- **Search**: `handleChangeSearchFiles` adds `query` with `name`, `is_recursive: true` when keyword non-empty.
- **Admin toolbar**: New folder (`api.createFolder`), upload (`viewUtil.uploadFile`), delete (`api.deleteFile`), download (`api.zipAndDownloadFiles` or single encrypted via URL), **Generate Folders** (`api.hydrateCompanyFolders`), **Grant Permissions** when `hasGrantPermission` from `api.isMember({ group_name: IT_SUPPORT })`.
- **Grant**: `handleClickGrantPermissions` → `GrantPermissionsModalContent`; `api.grantPermissions(companyId)` with `user_id`, `permissions[]`, and `selected_file` or `folder` (root folder **name**, e.g. `Accounting`).
- **Organize**: `interactjs` drag file → folder → `api.moveFile`; context menu **Move to Parent** → `moveFile` with parent from breadcrumbs.
- **Display**: Hides items where `lost == true && recovered == false`.

### Navigation / build

- `src/components/new-admin-side-menu.js`: **Accounting** → `href="/admin/accounting/"`, gated by `accounting.enabled`, `selected={activeMenuItemKey === "accounting"}`.
- `webpack/paths.js`: entry `admin/accounting/index` → `./src/views/admin/accounting/index.js`.
- `webpack/webpack.common.js`: outputs `admin/accounting/index.html`.

### `src/views/files/grant-permissions-modal.js`

- Same as admin Files: company users via `getCompanyUsers`; **View** (`can_view`) / **Edit** (`can_edit`) for selected user.
