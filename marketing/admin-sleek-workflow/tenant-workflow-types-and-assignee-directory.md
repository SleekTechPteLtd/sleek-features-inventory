# Tenant workflow types and assignee directory

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Tenant workflow types and assignee directory |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Marketing admin (authenticated staff using the Sleek admin workflow list) |
| **Business Outcome** | Staff see workflow-type filter choices that match the platform tenant, and can filter or reassign work using the same directory of admin groups and users the org exposes to the admin API. |
| **Entry Point / Surface** | **sleek-website** admin: **Workflow list** at `/admin/sleek-workflow/` — `WorkFlowList` in `index.js` with `AdminLayout` (`sidebarActiveMenuItemKey="camunda-workflow"`). Workflow-type options and assignee pickers live in `components/table.js` (filters and row-level assignee UI). |
| **Short Description** | On load, `getPlatformConfig()` supplies `tenant` (default `"sg"` if missing), stored on the list view and passed into the table. The table resolves workflow-type filter options from `CAMUNDA_WORKFLOW_TABLE_CONSTANTS.WORKFLOW_TYPE` using that tenant key, falling back to the `default` list when the tenant has no dedicated entry. Separately, `getAssignees()` loads every admin group via `api.getGroups()`, then for each group loads users with `api.getAdminsByGroup({ query: { group_id } })`, building grouped and flat option lists for filters and reassignment. |
| **Variants / Markets** | **Tenant-keyed workflow lists** in constants: `default` (broad SG-style set), `hk`, `gb` (UK incorporation + AU-style onboarding labels). Platform `tenant` values that do not match those keys use **`default`** via `lodash/get` fallback. **SG, HK, UK** align with those buckets; **AU** is not a separate `WORKFLOW_TYPE` key here — behavior falls under **`default`** unless platform maps AU differently in config (Unknown). |
| **Dependencies / Related Flows** | **Config**: `getPlatformConfig` (`config-loader.js` → `api.getPlatformConfig`). **Assignee data**: `GET /admin/groups`, `GET /admin/users/admins?group_id=…` (`api.getGroups`, `api.getAdminsByGroup`). **Consumes**: `components/table.js` (`initWorkflowTypes`, `assignedToList` / `assigneeGroups`), `components/assignee.js` (row reassignment → Camunda `updateAssignee`). **Related**: [Browse paginated workflow list](./browse-paginated-workflow-list.md) for list/query wiring. |
| **Service / Repository** | **sleek-website**: `src/views/admin/sleek-workflow/index.js`, `src/views/admin/sleek-workflow/constants/camunda-workflow-constants.js`, `src/views/admin/sleek-workflow/components/table.js`, `src/utils/api.js`. **Backend** implementing `/admin/groups` and `/admin/users/admins` — not read in this pass. |
| **DB - Collections** | **Unknown** from these views (groups and users via REST; no MongoDB references in the listed files). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact mapping from platform `tenant` string (e.g. `sg` vs `default` key) — `index.js` defaults to `"sg"` while `WORKFLOW_TYPE` uses `default`/`hk`/`gb`, so `sg` relies on `get(..., WORKFLOW_TYPE.default)`. Whether all environments expose the same group set for `getAdminsByGroup`. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/sleek-workflow/index.js`

- **`componentDidMount`**: `getPlatformConfig()` → `tenant = get(platformConfig, "tenant", "sg")` → `setState({ tenant })`.
- **`getAssignees`**: Calls `getGroupWithUsers()` which uses `api.getGroups()` then, per group, `api.getAdminsByGroup({ query: { group_id: group._id } })`, merging into `assigneeGroups` (`{ label: group.name, options: [...] }`) and a flat `assigneeOptions` list; failures per group resolve to `undefined` and are filtered out.
- **Pass-through**: `tenant`, `assigneeGroups`, and `assigneeOptions` are passed to `Table`; `updateAssignee` updates local row state after reassignment.

### `src/views/admin/sleek-workflow/constants/camunda-workflow-constants.js`

- **`CAMUNDA_WORKFLOW_TABLE_CONSTANTS.WORKFLOW_TYPE`**: Defines `default`, `hk`, and `gb` arrays of `{ label, value }` workflow slugs used for the workflow-type filter (distinct process families per region).

### `src/views/admin/sleek-workflow/components/table.js`

- **`initWorkflowTypes`** (called from `componentDidMount`): `setState({ workflowType: get(WORKFLOW_TYPE, this.props.tenant, WORKFLOW_TYPE.default) })` — tenant-scoped options with fallback to `default`.
- **Constructor**: `assignedToList: this.props.assigneeGroups` — seed from parent-loaded groups; used in `filterData` for the “Assigned to” column and `initAssignedToFlatList`.
- **`assigneeGroups`** is also passed through to the `Assignee` component for row-level reassignment (see `assigneeGroups={this.props.assigneeGroups}` near line 1011).

### `src/utils/api.js`

- **`getGroups`**: `GET ${getBaseUrl()}/admin/groups`.
- **`getAdminsByGroup`**: `GET ${getBaseUrl()}/admin/users/admins` with query `group_id` (via `getResource` options).
