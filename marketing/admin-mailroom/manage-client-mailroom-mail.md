# Manage client mailroom mail

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage client mailroom mail |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal operators (Admin) |
| **Business Outcome** | Operators can receive, file, and deliver client mail digitally by working in each company’s Mailroom folder tree and alerting the company owner when new mail is ready to view. |
| **Entry Point / Surface** | Sleek Admin > Mailroom (`/admin/mailroom/` — webpack entry `admin/mailroom` → `src/views/admin/mailroom.js`). |
| **Short Description** | After selecting a company, the operator works in the shared `FileExplorerView` scoped to the **Mailroom** root folder (newest files first). They can create subfolders, upload or drag-drop files, move items between folders, rename, search recursively, download (single file or zip), delete, generate missing standard folders, and grant file permissions (IT Support). When the sidebar context is Mailroom, an extra **Notify Owner** action sends email via the admin mailroom API. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Files**: `getFileBaseUrl()` — files microservice or legacy API (`files_microservice` platform config) for `GET/POST /files`, `/folders`, move/rename/zip/delete. **Main API**: `POST /admin/mailroom/notify-new-mail` (notify owner); `POST /admin/companies/:id/files/hydrate-root-folders` (generate folders); `POST .../files/permissions` (grant); `getCompanies` with admin layout for company picker. Related product: mailroom subscription during incorporation (`company_service_mailroom`) — separate flow. |
| **Service / Repository** | sleek-website; Sleek main API (`api.sleek.sg` / env); Files service (configurable `FILE_BASE_URL` / files MS) |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact MongoDB (or other) persistence for file metadata is owned by the files service / API and is not visible from sleek-website; confirm regional behaviour for notify-new-mail if needed. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Entry / shell**: `src/views/admin/mailroom.js` — mounts `FileExplorerView` with `sidebarActiveMenuItemKey="mailroom"`, `layoutType="admin"`, `rootFolderName="Mailroom"`, `sortFilesBy={["createdAt"]}`, `sortFilesOrder={[-1]}`, `companiesSelectIsVisible={true}`. Webpack: `webpack/paths.js` → `admin/mailroom`; `webpack.common.js` outputs `admin/mailroom/index.html`.
- **Company selection**: `file-explorer.js` — `renderCompaniesSelect` when `companiesSelectIsVisible`; `handleSelectCompany` → `fetchRootFolder` / `resetBreadcrumbs` / `fetchFiles`. `api.getCompanies({ query, admin: layoutType === "admin" })`.
- **Root folder**: `fetchRootFolder` — `api.getAllFiles` with `local_path: /companies/${selectedCompanyId}/`, `name: Mailroom` (uses last match).
- **Listing & sort**: `fetchFiles` — `api.getFiles` with `local_path`, `sort_by` / `sort_order` from props; paginates when count > 20.
- **Mailroom-only toolbar**: `renderSecondaryToolbarContent` — if `sidebarActiveMenuItemKey == "mailroom"`, appends **Notify Owner** (`handleClickNotifyOwner`).
- **Notify owner**: `handleClickNotifyOwner` — confirms dialog, then `api.mailroomNotifyNewMail({ body: JSON.stringify({ company_id: selectedCompanyId }) })`.
- **API client**: `src/utils/api.js` — `mailroomNotifyNewMail` → `POST ${getBaseUrl()}/admin/mailroom/notify-new-mail`. File ops: `getFiles`, `getAllFiles`, `createFolder` (`/folders`), `uploadFile`, `moveFile`, `renameFile`, `deleteFile`, `zipAndDownloadFiles` against `getFileBaseUrl()`. `hydrateCompanyFolders(companyId)` → `POST /admin/companies/${companyId}/files/hydrate-root-folders`. `grantPermissions` → `POST /admin/companies/${companyId}/files/permissions`.
- **Admin-only actions**: `user.profile === "admin"` gates new folder, upload, delete, notify, generate folders, grant permissions, drag-drop setup; download/search available broadly.
- **Generate folders**: `handleClickGenerateFolders` — `api.hydrateCompanyFolders(selectedCompanyId)` after confirmation.
