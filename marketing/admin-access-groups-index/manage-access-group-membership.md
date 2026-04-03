# Manage access group membership

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage access group membership |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (Sleek Admin operator with **full** `access_management` permission) |
| **Business Outcome** | Registered users are assigned to the correct access groups so platform permissions match policy; when SSO owns group membership, operators can still audit rosters without changing them in-app. |
| **Entry Point / Surface** | **sleek-website** admin: **Access → Groups** at `/admin/access/groups/` — `AdminLayout` with `sidebarActiveMenuItemKey="access"` and `sidebarActiveMenuSubItemKey="groups"`. |
| **Short Description** | Loads all access groups (excluding the hidden `sleek-user` slug) and, per group, paginates members via admin user listing filtered by `group_id`. Operators **add** a registered user by email or **remove** a member from the group using admin APIs. Add/remove is disabled when CMS SSO `allow_group_management` is false or the signed-in user lacks full access management; the UI explains that management moved to JumpCloud. Optional **Edit staff profile** per row when CMS `user_management` enables `pages.groups`. |
| **Variants / Markets** | **Unknown** without CMS/platform snapshot; Sleek environments often span **SG, HK, UK, AU** — SSO and permission flags are tenant-specific. |
| **Dependencies / Related Flows** | **`api.getGroups`** → `GET /admin/groups`. **`api.getAdminsByGroup`** → `GET /admin/users/admins` (query: `group_id`, pagination `limit`/`page`, `include_pagination_metadata`). **`api.addToGroup`** → `PUT /admin/users/add-to-group` (body: `email`, `group_id`). **`api.removeFromGroup`** → `PUT /admin/users/:userId/remove-from-group` (body: `group_id`). Session: **`getUser`** (from `views/admin/common`). Platform config: **`getPlatformConfig`**, **`getAppFeatureProp`** for `sso` (`value.allow_group_management`) and `user_management` / `partner_access_management`. **Co-located on same page** (separate capabilities): “Login As…” and “Login As Partner” use other forms/APIs — not part of group membership. |
| **Service / Repository** | **sleek-website**: `src/views/admin/access/groups/index.js`, `src/views/admin/access/groups/access-group-user.js`, `src/views/admin/access/groups/access-add-user-form.js`, `src/utils/api.js`, `src/views/admin/components/edit-staff-profile/edit-staff-profile.js` (conditional). Backend implementing `/admin/groups`, `/admin/users/admins`, add/remove group membership (not in this repo). |
| **DB - Collections** | **Unknown** in this repo; backend persists groups and user–group links — confirm in API service (likely user/group collections). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High (admin surface); Medium for add/remove frequency when SSO `allow_group_management` is often false in production. |
| **Disposition** | Unknown |
| **Open Questions** | Exact RBAC and data model on backend for `/admin/users/admins` and group membership mutations. Whether `getGroupUsers` in `index.js` (commented out) is legacy or planned — live path loads users inside `AccessGroupUser` only. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/access/groups/index.js` (`AdminAccessGroupsView`)

- **Mount**: `getPlatformConfig` → `getUser` → `getGroups`; computes `disableUserManagement` from SSO `sso.value.allow_group_management` and `user.permissions.access_management === "full"` (in dev, `process.env.IS_SSO_ENABLED` can override SSO enabled flag).
- **`getGroups`**: `api.getGroups()` → filters out `HIDDEN_GROUPS` including `"sleek-user"`.
- **`handleAddUserClick`**: Opens dialog with `AccessAddUserForm` for `groupId`.
- **`handleRemoveUserClick`**: Confirmation dialog → `api.removeFromGroup(userId, { body: JSON.stringify({ group_id }) })`.
- **`renderGroupUsers`**: One `AccessGroupUser` per group with `disableUserManagement`, `onAddUserClick`, `onRemoveUserClick`.
- **Toolbar** (not membership): “Login As…”, “Login As Partner” (if `partner_access_management` enabled) — separate from group roster management.

### `src/views/admin/access/groups/access-group-user.js` (`AccessGroupUser`)

- **`paginateGroupUsers`**: `getAdminsByGroup({ query: { group_id, include_pagination_metadata: true, limit: 100, page } })`; appends `result`, follows `metadata.next_page` with staggered `setTimeout` calls. Table columns: email, `registered_at` (formatted), Remove + optional `EditStaffProfile`.
- **Add**: “Add User By Email” → `onAddUserClick(group._id)`; disabled when `disableUserManagement`; tooltip: “User group management is moved to JumpCloud”.
- **Remove**: Same disable + tooltip when management disabled.

### `src/views/admin/access/groups/access-add-user-form.js` (`AccessAddUserForm`)

- **Submit**: `api.addToGroup({ body: JSON.stringify({ email, group_id: props.groupId }) })` → success toast via `onSuccess`.

### `src/utils/api.js`

- **`getGroups`**: `GET ${getBaseUrl()}/admin/groups`
- **`getAdminsByGroup`**: `GET ${getBaseUrl()}/admin/users/admins`
- **`addToGroup`**: `PUT ${getBaseUrl()}/admin/users/add-to-group`
- **`removeFromGroup`**: `PUT ${getBaseUrl()}/admin/users/${userId}/remove-from-group`
