# Manage internal staff users

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage internal staff users |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal operators (Sleek Admin / staff with User Management access) |
| **Business Outcome** | Staff identity shown to customers stays accurate: roster is limited to configured staff types, and operators can correct display names and profile photos used across the product. |
| **Entry Point / Surface** | **sleek-website** admin: **User Management** (`/admin/user-management/`) — `AdminLayout` with `sidebarActiveMenuItemKey="user-management"`; primary toolbar title “User Management”. |
| **Short Description** | Loads all staff users for types derived from CMS `support.staffAssigneeMapping` (via `getAppFeatureProp` on `platformConfig.cmsGeneralFeatureList`). Presents a table with name, email, joined date, photo presence (YES/NO chips), and an **Edit** action per row. Client-side filters: name and email (substring, case-insensitive), optional photo filter (YES/NO). **Edit staff profile** dialog edits “Display name in Customer App”, uploads/crops/removes JPG/PNG photo (≤5MB), then persists via user update and optional file upload. |
| **Variants / Markets** | Staff **types** are tenant/CMS-driven (`staffAssigneeMapping`). Sleek markets **SG, HK, UK, AU** typical; exact type sets per environment — **Unknown** without CMS snapshot. |
| **Dependencies / Related Flows** | **`api.getAllStaffUsers`** → `GET /admin/staff-users?types=…` (types from platform config). **`api.updateUser`** → `PUT /users/:userId` with JSON body (`display_name`, `profile_pic`). **`viewUtil.uploadProfilePic`** → **`api.uploadProfilePic`** → `POST` files service `/files/upload-profile-pic` (multipart: `file`, `displayed_name`, `user_id`). Session gate: **`api.getUser`**; unverified email redirects to `/verify/`. **`store.get("platformConfig")`** for CMS feature list. |
| **Service / Repository** | **sleek-website**: `src/views/admin/user-management/index.js`, `src/views/admin/user-management/components/users-table.js`, `src/views/admin/components/edit-staff-profile/edit-staff-profile.js`, `src/utils/api.js`, `src/utils/view.js` (`uploadProfilePic`). **sleek-back** / file service (not in this repo): admin staff-users listing, user mutation, profile-pic storage. |
| **DB - Collections** | **Unknown** in this repo; backend user/staff records (likely MongoDB `User` or equivalent) — confirm in sleek-back admin staff-users and user controllers. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `handlePaginationClicked` / `handleRowsPerPageChanged` in `UserManagementList` are fully wired (table uses client-side `filteredUsers` only; `getAdminUsers` does not pass pagination to the API; `handleRowsPerPageChanged` references `loadTransactions`, which is undefined in this file — possible dead/broken path). Exact RBAC for `/admin/staff-users` and `/users/:id` on backend. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/user-management/index.js` (`UserManagementList`)

- **Mount**: `domready` → `ReactDOM.render` into `#root`.
- **`getUser`**: `api.getUser()`; if `registered_at` is null, redirect `/verify/`; else `setState({ user })`.
- **`getAdminUsers`**: Reads `platformConfig` from `store.get("platformConfig")`; `support = getAppFeatureProp(..., "support")`; `staffAssigneeMapping = get(support, "value.staffAssigneeMapping", [])`; `staffTypes = staffAssigneeMapping.map(staff => staff.type)`; **`api.getAllStaffUsers(staffTypes)`**; sets `users` from `response.data`. `total` fixed at `0`; loading flag toggled.
- **Layout**: `AdminLayout` `hideDrawer={true}`, `sidebarActiveMenuItemKey="user-management"`, toolbar “User Management”.
- **Child**: `UsersTable` receives `users`, `getAdminUsers`, `handleFilterChanged` (audit-log–style filters present in parent but staff table uses its own header filters).

### `src/utils/api.js`

- **`getAllStaffUsers(types = [])`**: `GET ${getBaseUrl()}/admin/staff-users?types=${types.join(",")}` via `getResource`.
- **`updateUser(userId, options)`**: `PUT ${getBaseUrl()}/users/${userId}` via `putResource` (JSON body from caller).
- **`uploadProfilePic(options)`**: clears `Content-Type` for multipart; `POST ${getFileBaseUrl()}/files/upload-profile-pic`.

### `src/views/admin/user-management/components/users-table.js` (`CustomPaginationActionsTable`)

- **Columns** (`USER_MANAGEMENT_TABLE_HEADERS`): Name, Email, Joined date (`moment(registered_at)`), Photo (chip YES/NO from `user.profile_pic`), Edit.
- **Client filters** (`updateFilteredUsers`): `name` = `first_name + " " + last_name`, `email`; optional third condition when photo filter set: `YES` → must have `profile_pic`, `NO` → must not.
- **Row**: `EditStaffProfile` with `user`, `onReloadData={this.onReloadData}` — updates local `filteredUsers` when `_id` matches (`profile_pic`, `display_name`).

### `src/views/admin/components/edit-staff-profile/edit-staff-profile.js` (`EditStaffProfile`)

- **Dialog**: “Edit staff profile”; fields include **Display name in Customer App** (`display_name`), photo with **react-cropper**, 5MB limit, remove photo confirmation.
- **`handleSaveChanges`**: If new file: **`viewUtil.uploadProfilePic(user._id, file, display_name)`** then build payload with `profile_pic` path from upload response; else payload `{ display_name }`. **`api.updateUser(user._id, { body: JSON.stringify(payload) })`**; `onReloadData(response.data)`.
- **`handleYesRemovePhoto`**: `payload = { profile_pic: '' }`; `api.updateUser`; `onReloadData`.
- **Snackbar** on success with message including staff `first_name` / `last_name`.

### `src/utils/view.js`

- **`uploadProfilePic(userId, file, displayedName)`**: `FormData` with `file`, `displayed_name`, `user_id` → `api.uploadProfilePic`.
