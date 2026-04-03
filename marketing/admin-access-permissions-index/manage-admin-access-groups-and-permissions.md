# Manage admin access groups and permissions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage admin access groups and permissions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations user (Sleek admin operator with **full** `access_management` permission on their own user record) |
| **Business Outcome** | Internal teams can define named access groups, optional parent relationships, and per-admin-resource permission levels so who can do what in the admin app stays accurate and auditable. |
| **Entry Point / Surface** | **sleek-website** admin: **Access → Permissions** — `AdminLayout` with `sidebarActiveMenuItemKey="access"` and `sidebarActiveMenuSubItemKey="permissions"` (view mounted at `src/views/admin/access/permissions/index.js`). |
| **Short Description** | Lists all access groups (slug, display name, parent). Operators with full access management can add groups, edit metadata and parent, delete non-system groups, and open a popover to set each group’s role matrix: **full**, **edit**, **read**, or **none** per `ADMIN_RESOURCES` area (companies, files, mailroom, requests, services, invoices, users, workflows, partner access, business account, etc.). System groups cannot be edited or deleted. Files/mailroom levels are constrained when Companies is `none`. Optional **Business Account** row is hidden unless CMS enables the feature. |
| **Variants / Markets** | **Unknown** without CMS/platform snapshot; Sleek environments often span **SG, HK, UK, AU** — feature flags (e.g. `business_account`, KYC label for invitation override) are tenant-specific. |
| **Dependencies / Related Flows** | **Same domain as** Access → Groups (membership to these groups is managed elsewhere). **APIs**: `getGroups`, `createGroup`, `updateGroup`, `deleteGroup` on `${getBaseUrl()}/admin/groups` (`src/utils/api.js`). User session via `getUser` (`views/admin/common`). Permission matrix driven by `ADMIN_RESOURCES` and platform config (`getAppFeatureProp` for `business_account`, `kyc_status` label tweak). Backend owns persistence and enforcement of roles for signed-in admin users. |
| **Service / Repository** | **sleek-website**: `src/views/admin/access/permissions/index.js`, `access-group-manager.js`, `access-group-form.js`, `access-permission-button.js`, `src/utils/api.js`, `src/utils/constants.js` (`ADMIN_RESOURCES`). Backend implementing `/admin/groups` (not in this repo). |
| **DB - Collections** | **Unknown** in this repo; groups and embedded `role` maps are persisted server-side — confirm collection/schema in the API service. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High for the admin surface; Medium for how often operators change matrices vs. one-time setup. |
| **Disposition** | Unknown |
| **Open Questions** | Whether backend normalizes missing `role` keys when older groups omit newer resources (`perform_kyc`, `accounting_management`, etc.). Exact validation rules for parent group selection (cycles, depth). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/access/permissions/index.js` (`AdminAccessPermissionsView`)

- **Mount**: `getUser` → `api.getGroups()` → `setState({ groups: res.data })`.
- **Add Group**: `handleAddGroupClick` opens dialog with `AccessGroupForm`; **Add Group** toolbar button disabled unless `user.permissions.access_management === "full"`.
- **Edit / Delete**: `handleEditGroupClick` / `handleDeleteGroupClick`; delete confirms then `api.deleteGroup(groupId)`.
- **Success path**: `getGroups` refresh, `BottomToaster`, `closeDialog`.

### `src/views/admin/access/permissions/access-group-manager.js` (`AccessGroupManager`)

- **Table**: Columns Slug, Group, Is Part Of (`group.parent.name`), Permissions (`AccessPermissionButton`), actions.
- **Edit/Delete**: Disabled when `group.is_system_group === true` or `user.permissions.access_management !== "full"`.

### `src/views/admin/access/permissions/access-group-form.js` (`AccessGroupForm`)

- **Fields**: `name`, `group_slug`, `parent_id` (select from all groups; empty = no parent).
- **Create**: `api.createGroup({ body: JSON.stringify({ group_slug, name, parent_id }) })`.
- **Update**: `api.updateGroup(group._id, { body: JSON.stringify({ group_slug, name, parent_id }) })`.

### `src/views/admin/access/permissions/access-permission-button.js` (`AccessPermissionButton`)

- **Popover**: Renders matrix from `ADMIN_RESOURCES` (`src/utils/constants.js`): radio columns Full / Edit / Read / None per resource; `refreshRole` syncs from `props.role` on mount and when popover opens.
- **Cross-rules**: For `files` and `mailroom`, Full/Edit radios disabled when `role.companies === "none"`.
- **Apply**: `api.updateGroup(groupId, { body: JSON.stringify({ role: this.state.role }) })`.
- **Gating**: Popover and **Manage Permissions** disabled unless `user.permissions.access_management === "full"`.
- **CMS**: Hides Business Account row when `business_account` feature not enabled; relabels invitation override when `kyc_status` version is 2.

### `src/utils/api.js`

- **`getGroups`**: `GET ${getBaseUrl()}/admin/groups`.
- **`createGroup`**: `POST ${getBaseUrl()}/admin/groups`.
- **`updateGroup`**: `PUT ${getBaseUrl()}/admin/groups/:groupId`.
- **`deleteGroup`**: `DELETE ${getBaseUrl()}/admin/groups/:groupId`.
