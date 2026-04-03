# Manage recovery file storage

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage recovery file storage |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal admins (`user.profile === "admin"`) and company owners (`isUserOwnerOrAdmin`); others see a no-permission state |
| **Business Outcome** | Recovery artifacts for mailroom work stay in a dedicated `recovery-files` folder tree so staff can browse, search, download, reconcile to client documents, and (as admins) curate folders and files without losing context when switching company. |
| **Entry Point / Surface** | Sleek Admin — Mailroom sidebar context (`sidebarActiveMenuItemKey="mailroom"`) — webpack entry `admin/recovery/recovery-files` → `src/views/admin/recovery/recovery-files.js`, output `admin/recovery/recovery-files/index.html`. Optional query `?path=...` for deep links; `?cid=` seeds `company_id` in local storage. |
| **Short Description** | The **RecoveryFileExplorerView** loads dashboard session data via `viewUtil.fetchDashboardCommonData()`, resolves the virtual root folder named `recovery-files` under `/`, then lists child files through **`GET ${getBaseUrl()}/admin/recovery/files`** (`api.getAllRecoveryFiles`, paginated). Users navigate with breadcrumbs and back control, open folders (double-click), search by name with **`is_recursive: true`**, download non-folder files via the files base URL, and use keyboard arrows to move selection. **Admins** additionally create folders, upload (input or drag-drop, max 5 MB per `uploadRecoveryFile` with `is_recovery_file: true`), move items (drop onto folders or “Move to Parent”), rename, and delete — all against the shared files service (`createFolder`, `moveFile`, `renameFile`, `deleteFile` on `getFileBaseUrl()`). **RecoveryFile** previews in an overlay and supports reconcile / unreconcile / mass-reconcile against **`POST /admin/recovery/reconcile-files`** and **`POST /admin/recovery/unreconcile-files`**, with card colouring from match scores and reconciled state. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Main API**: `GET /admin/recovery/files` (list); `POST /admin/recovery/reconcile-files`; `POST /admin/recovery/unreconcile-files`. **Files service** (same as Mailroom): `POST ${FILE_BASE_URL}/files` (upload with `parent_folder_id`, recovery flag), `DELETE/PATCH/...` on `/files/:id`, `/files/:id/move`, `/files/:id/rename`, `POST /folders`. **Session**: `viewUtil.fetchDashboardCommonData`, `viewUtil.isUserOwnerOrAdmin`, `viewUtil.downloadFile`, `viewUtil.uploadRecoveryFile`. Closely related to **client mailroom** and recovery reconciliation workflows; not the same root folder as Mailroom (`Mailroom` vs `recovery-files`). |
| **Service / Repository** | sleek-website; Sleek main API (`getBaseUrl()`); files microservice / `FILE_BASE_URL` (`getFileBaseUrl()`) |
| **DB - Collections** | Unknown (file and recovery metadata persist behind main API and files service; not visible from this frontend repo) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether non-owner operators are intended to use this UI in some deployments — current gate is owner-or-admin only. Confirm whether a variant should expose `companiesSelectIsVisible` for multi-company picking (default mount omits it; company context may still change via admin layout). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Shell / mount**: `src/views/admin/recovery/recovery-files.js` — `domready` renders `RecoveryFileExplorerView` with `sidebarActiveMenuItemKey="mailroom"`, `layoutType="admin"`, default sort `createdAt` / `-1`. Webpack: `webpack/paths.js` entry `admin/recovery/recovery-files`; `webpack.common.js` HTML `admin/recovery/recovery-files/index.html`.
- **Permission gate**: `renderBodyContent` — if `viewUtil.isUserOwnerOrAdmin(user, companyUsers)` is false, `NonIdealState` with `FILE_MESSAGES["no_permission"]`; otherwise `#file-explorer` with file list and overlay.
- **Root & listing**: `fetchRootFolder` → `fetchFileFromPathAndName("/", "recovery-files")` using `api.getAllRecoveryFiles({ query: { local_path, name } })` and `last(files)`. `fetchFiles` / `fetchFilesFromPath` — `getAllRecoveryFiles` with `local_path`, `sort_by` / `sort_order`; updates `?path=` via `history.pushState`.
- **Admin toolbar**: `renderSecondaryToolbarContent` — if `user.profile === "admin"`: New Folder (`api.createFolder`), Upload (`uploadRecoveryFile` → `api.uploadFile` with `is_recovery_file`), Delete (`api.deleteFile`). Download and Mass-Reconcile shown more broadly; search field calls `fetchFiles` with `{ name, is_recursive: true }` when keyword set.
- **Drag-and-drop (admin)**: `componentDidMount` registers drag listeners; `setupFileDragAndDrop` uses `interactjs` — drop on `.item[data-type='folder']` calls `api.moveFile` with `destination_folder`.
- **Context menu**: `handleContextMenuFile` — Download, Get Info; for admin: Rename (`api.renameFile`), Move to Parent (`api.moveFile`), Delete.
- **Upload helpers**: `src/utils/view.js` — `uploadRecoveryFile` appends `is_recovery_file: true` to `FormData` alongside `parent_folder_id`; shares `downloadFile` and `fetchDashboardCommonData` / `isUserOwnerOrAdmin` with other admin views.
- **Per-file UI**: `src/views/admin/recovery/recovery-file.js` — `RecoveryFile` card; double-click folder → `openFolder`; file → `displayOverlay` with iframe preview from `api.downloadFile` blob URL; reconcile flows call `api.reconcileFiles` / `api.unreconcileFiles`; `getSingleMatchingFile` supports mass reconcile from parent.
- **API client**: `src/utils/api.js` — `getRecoveryFiles` / `getAllRecoveryFiles` → `GET ${getBaseUrl()}/admin/recovery/files`; `reconcileFiles` / `unreconcileFiles` paths under `/admin/recovery/`; file mutations on `getFileBaseUrl()` as listed above.
