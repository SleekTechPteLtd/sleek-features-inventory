# Reconcile recovery files to client records

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Reconcile recovery files to client records |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal operators (Admin); owner/admin for same-company access gate |
| **Business Outcome** | Recovered mail and documents in the recovery bucket can be linked to the correct company or user file so downstream client mailroom and filing stay accurate. |
| **Entry Point / Surface** | Sleek Admin > Mailroom context — **File Recovery** (`/admin/recovery/recovery-files/` with optional `?cid=` / `?path=`; webpack entry `admin/recovery/recovery-files` → `src/views/admin/recovery/recovery-files.js`). |
| **Short Description** | Operators browse the **recovery-files** virtual folder tree (same file-explorer pattern as mailroom), preview items in an overlay, and reconcile each recovery file to a target client file or unreconcile an existing link. Cards are colour-coded by reconciliation state, match count, and potential-match scores. **Mass-Reconcile** runs `singleReconcile()` only for files that have exactly one `matchingFiles` entry and are not yet reconciled. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Main API**: `GET /admin/recovery/files` (paginated listing); `POST /admin/recovery/reconcile-files`; `POST /admin/recovery/unreconcile-files` with `recovery_file_id` + `target_file_id`. **Files service**: `getFileBaseUrl()` — preview/download/upload/move/rename/delete via `/files` and related file endpoints (shared with admin mailroom file explorer). **Companies**: `api.getCompanies` when `companiesSelectIsVisible` (not enabled in default mount). Optional URL `?cid=` seeds `company_id` in local storage. Related: admin recovery report download lives on a separate view (`admin/recovery` → CSV). |
| **Service / Repository** | sleek-website; Sleek main API (`getBaseUrl()`); files microservice / file API (`getFileBaseUrl()`) |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Persistence and matching logic for `matchingFiles` / `potential_match_files` / `reconciled_files` live server-side; Mass-Reconcile preview dialog references `match.user.last_name` alongside `match.matchingFile.user` — likely a front-end bug if `match.user` is undefined. Confirm intended operator roles vs `viewUtil.isUserOwnerOrAdmin` gate. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Shell**: `src/views/admin/recovery/recovery-files.js` — `RecoveryFileExplorerView` with `sidebarActiveMenuItemKey="mailroom"`, `layoutType="admin"`; mounts on `#root`. Root folder resolved via `fetchFileFromPathAndName("/", "recovery-files")` + `api.getAllRecoveryFiles`.
- **Listing**: `getAllRecoveryFiles` → `GET ${getBaseUrl()}/admin/recovery/files` with query (`local_path`, `sort_by`, `sort_order`, optional `name` + `is_recursive` for search). Breadcrumbs sync `?path=` in history.
- **Mass reconcile**: `handleMassReconcile` — collects refs where `getSingleMatchingFile()` returns the lone `matchingFiles[0]`, shows dialog, `Promise.all` on `singleReconcile()` → `reconcileAndGetNewState` → `POST .../reconcile-files`.
- **Per-file UI**: `src/views/admin/recovery/recovery-file.js` — `getCardBackgroundColor` uses `reconciled_files`, `potential_match_files` (filtered vs reconciled), `matchingFiles` length and score thresholds; preview strip shows user or company; double-click opens overlay with iframe preview.
- **Reconcile**: `reconcileFiles` / `reconcileAndGetNewState` — `POST` body `{ recovery_file_id, target_file_id }` where `target_file_id` is `targetFile.file._id`; local state moves entry into `reconciled_files` and removes from `matchingFiles`. Potential matches rendered when valid potential matches exist; else full `matchingFiles` list.
- **Unreconcile**: `unreconcileFiles` / `unreconcileAndGetNewState` — `POST .../unreconcile-files`; filters `reconciled_files`, may push back into `matchingFiles`.
- **API client**: `src/utils/api.js` — `getRecoveryFiles` / `getAllRecoveryFiles`, `reconcileFiles`, `unreconcileFiles` endpoints as above.
- **Admin-only toolbar**: New folder, upload, delete, drag-drop — `user.profile === "admin"`; download and search broader. `viewUtil.isUserOwnerOrAdmin` gates entire body vs permission message.
- **Webpack**: `webpack/paths.js` entry `admin/recovery/recovery-files`; `webpack.common.js` outputs `admin/recovery/recovery-files/index.html`.
