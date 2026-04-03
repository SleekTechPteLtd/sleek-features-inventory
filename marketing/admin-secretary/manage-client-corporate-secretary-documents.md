# Manage client corporate secretary documents

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage client corporate secretary documents |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations staff (Sleek admin users with `profile === "admin"`); **Grant Permissions** UI requires **IT Support** group membership (`api.isMember` with `SLEEK_GROUP_NAMES.IT_SUPPORT`). |
| **Business Outcome** | Operations can select a client company and work in that company’s **Secretary** folder tree so corporate secretary files stay browsable, organized, and accessible—without mixing this work with other admin file surfaces. |
| **Entry Point / Surface** | **sleek-website** admin: **Secretary** — `/admin/secretary/` (`webpack` chunk `admin/secretary` → `src/views/admin/secretary.js`). Uses `AdminLayout` with `sidebarActiveMenuItemKey="secretary"`. Optional `?cid=` sets `company_id` in local storage; optional `?folder=` deep-links into a named subfolder then clears the query string. |
| **Short Description** | Same **FileExplorerView** capability as admin **Files** (`/admin/files/`): filterable company picker, root folder named **Secretary** under `/companies/{companyId}/`, breadcrumbs, recursive name search, upload (picker and admin drag-drop), download (zip or single `encrypted_s3`), new folder, rename, delete (multi-select when CMS `multi_file_delete` is on), preview overlay, drag-drop move between folders, **Generate Folders** (hydrate missing roots), and **Grant Permissions** for IT Support. Mailroom-only actions (e.g. **Notify Owner**) are tied to `sidebarActiveMenuItemKey === "mailroom"` and do not appear here. |
| **Variants / Markets** | Company-scoped; **SG, HK, UK, AU** not encoded in these views — **Unknown** for market-specific behaviour. |
| **Dependencies / Related Flows** | **Shared implementation** with `marketing/admin-files-index/manage-company-documents-admin-secretary.md` (same `FileExplorerView` and **Secretary** root; differs only by admin route and sidebar key). **File service**: `getFiles`, `getAllFiles`, `createFolder`, `moveFile`, `renameFile`, `deleteFile`, `zipAndDownloadFiles`, `downloadFile` / file URLs via `getFileBaseUrl()`. **Main API**: `getCompanies` with `admin: true`, `hydrateCompanyFolders`, `grantPermissions`, `isMember` (IT Support). **Customer dashboard** file explorer reuses `FileExplorerView` with non-admin `layoutType` (not this surface). |
| **Service / Repository** | **sleek-website**: `src/views/admin/secretary.js`, `src/views/file-explorer.js`, `src/views/files/grant-permissions-modal.js`, `src/utils/api.js`, `src/utils/view.js`. **File microservice** and **sleek-back** (hydrate, permissions, persistence): not in this repo. |
| **DB - Collections** | **MongoDB** (or other stores) for files, folders, and permissions — **Unknown** from sleek-website; persistence lives behind file and admin APIs. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether **Secretary** vs **Files** nav entries are intentionally redundant for the same tree, or if product intends to consolidate. Same as related doc: exact RBAC vs `user.permissions.files` / `companies` for **Generate Folders** vs backend enforcement; status of `lost` / `recovered` file flags. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/secretary.js`

- Mounts `FileExplorerView` with `sidebarActiveMenuItemKey="secretary"`, `layoutType="admin"`, `rootFolderName="Secretary"`, `sortFilesBy={["name"]}`, `sortFilesOrder={[1]}`, `companiesSelectIsVisible={true}` — identical props to `src/views/admin/files/index.js` except the sidebar key (and thus active nav highlight / mailroom-gated toolbar items).

### `src/views/file-explorer.js` (`FileExplorerView`)

- **Layout**: `layoutType === "admin"` → `AdminLayout`.
- **Company selection**: `companiesSelectIsVisible` → Blueprint `Select`; `api.getCompanies({ query: { name }, admin: true })` as user types.
- **Root**: `fetchRootFolder` → `api.getAllFiles` with `local_path: /companies/{selectedCompanyId}/`, `name: rootFolderName` (**Secretary**); uses last match.
- **Listing / search**: `fetchFiles` → `api.getFiles` with paging in steps of 20; search adds `name` + `is_recursive: true`.
- **Admin actions**: `createFolder`, upload via `viewUtil.uploadFile`, `deleteFile`, `zipAndDownloadFiles` / direct URL for `encrypted_s3`, `hydrateCompanyFolders`, `grantPermissions` (with `GrantPermissionsModalContent`), `moveFile` (context menu, breadcrumbs, drag-drop).
- **IT Support**: `hasGrantPermission` from `api.isMember({ group_name: IT_SUPPORT })`.
- **Display**: Hides items with `lost == true && recovered == false`.

### `src/utils/api.js` (calls used)

- File endpoints: `getFiles`, `getAllFiles`, `createFolder`, `moveFile`, `renameFile`, `deleteFile`, `zipAndDownloadFiles`, `downloadFile`; base URL from `getFileBaseUrl()`.
- Admin: `hydrateCompanyFolders` → `POST .../admin/companies/{companyId}/files/hydrate-root-folders`; `grantPermissions` → `POST .../admin/companies/{companyId}/files/permissions`.

### Routing and navigation

- **Webpack**: `paths.js` entry `admin/secretary` → `./src/views/admin/secretary.js`; outputs `admin/secretary/index.html`.
- **Mobile admin menu**: `src/components/mobile-admin-user-menu.js` — **Secretary** → `href="/admin/secretary/"`.
