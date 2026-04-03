# Review corp sec role assignments

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Review corp sec role assignments |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corp Sec operators (Sleek Admin users); **Sleek Admin** group members can select any Corp Sec member when allocation permission is `none` or `read` |
| **Business Outcome** | Corporate secretarial staff can see which companies a chosen team member owns as **CS in charge** or **CS backup**, filter by company status, see transfer flags, and jump to company admin records for follow-up—without guessing portfolio coverage. |
| **Entry Point / Surface** | **sleek-website** admin: **Corp Sec** → **My Tasks** (`/admin/corpsec/my-tasks/`). Shown when CMS `corpsec.my_tasks` is enabled (`AdminCorpsecSideSubMenu`). `AdminLayout` with `sidebarActiveMenuItemKey="my-tasks"`, `hideDrawer={true}`; primary toolbar breadcrumb **Tasks**. |
| **Short Description** | Two side-by-side **RoleAllocation** blocks (**CS in charge** and **CS Backup**) load Corp Sec members (`getAdminsByGroup` → `GET /admin/users/admins` with `group_name: Corp Sec`). Each block lists companies for the selected user and role type via **`GET /admin/user/{userId}/resource-allocation-role/{roleType}`** (`roleType`: `cs-in-charge` or `cs-backup`), with optional **`company_status`** query from the status filter. Rows show company name (link to company edit), label for **Company Status**, and **Transfer** (`is_transfer` → Yes/No). Users with `permissions.allocation` of `none` or `read` are locked to themselves unless they are in **Sleek Admin** (`forceEnableMemberSelection`), in which case the member dropdown stays enabled. Company status options come from CMS **`admin_constants.COMPANY_STATUSES`**. Pagination controls in the table UI are commented out. |
| **Variants / Markets** | Unknown — no market branching in these views; admin API host follows global `getBaseUrl()`. |
| **Dependencies / Related Flows** | **Upstream**: Session user (`getUser`), platform config (`getPlatformConfig`), CMS **Corp Sec** features (`my_tasks`, `COMPANY_STATUSES`). **API** (`src/utils/api.js`): `getAdminsByGroup`, `getUserResourceAllocations`. **Downstream**: Company admin at **`/admin/companies/edit/?cid={companyId}`** from each row. **Related**: `common.js` also exports **`getCompanies`** (admin company list with `corpsec_pic` / `corpsec_backup` query) but the current **RoleAllocation** path does not import it—only **`getUserAllocationRolesByType`** is used. **Parallel**: Non–Corp Sec **My Tasks** bundle (`admin/my-tasks/index`) reuses the same `RoleAllocation` pattern. |
| **Service / Repository** | **sleek-website**: `src/views/admin/corpsec/my-tasks/index.js`, `roleAllocation.js`, `table.js`, `taskRow.js`, `common.js`; `src/views/admin/common` (pagination handlers re-used but pagination UI disabled in `table.js`); `src/utils/api.js`. **Backend** (not in repo): admin user and resource-allocation endpoints behind `getBaseUrl()`. |
| **DB - Collections** | Unknown from this frontend — persistence is behind admin APIs; collections not named in sleek-website. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact JSON shape returned by **`getUserResourceAllocations`** (e.g. whether `response.data` is a list or wraps `count` + list): `roleAllocation` sets `companies: response.data` and `pageMax` from `response.data.count`, which is inconsistent if `data` is only an array. Whether the stray `options = ` text in **`table.js`** `<select>` children is intentional or a rendering bug. Whether **`getCompanies`** in `common.js` is still used elsewhere or legacy. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/corpsec/my-tasks/index.js` (`MyTasksView`)

- **Mount**: `componentDidMount` → `getPlatformConfig`, `getUser`, `getCorpSecMembers` (`group_name: Corp Sec`), `getSleekAdminMembers` (`group_name: Sleek Admin`); if current user is in Sleek Admin, `forceEnableMemberSelection: true`.
- **Body**: Reads `COMPANY_STATUSES` from `cmsGeneralFeatureList` → `admin_constants`. Renders two **`RoleAllocation`** instances with `roleType` **`cs-in-charge`** and **`cs-backup`**, passing `companyStatuses`, `members`, `user`, and `forceEnableMemberSelection`.

### `src/views/admin/corpsec/my-tasks/roleAllocation.js` (`RoleAllocation`)

- **Initial member**: Picks first Corp Sec member other than the logged-in user when possible; otherwise current user.
- **Permission gating**: If `user.permissions.allocation` is **`none`** or **`read`**, locks selection to self and disables dropdown unless **`forceEnableMemberSelection`** (Sleek Admin).
- **Data load**: **`getUserAllocationRolesByType`** → `getUserResourceAllocations(userId, roleType, { query: { company_status? } })` from `./common`.
- **Handlers**: Member and company-status select changes refetch; pagination handlers bound from `../../common` (UI not surfaced in `table.js`).

### `src/views/admin/corpsec/my-tasks/common.js`

- **`getUserAllocationRolesByType`**: Builds `options.query` with optional **`company_status`**; calls **`api.getUserResourceAllocations`**.
- **`getCompanies`**: Admin **`api.getCompanies`** with `corpsec_pic` / `corpsec_backup` and pagination/sort — not referenced by **`roleAllocation.js`** in this folder.

### `src/utils/api.js`

- **`getAdminsByGroup`**: `GET ${getBaseUrl()}/admin/users/admins`.
- **`getUserResourceAllocations`**: `GET ${getBaseUrl()}/admin/user/${userId}/resource-allocation-role/${resourceAllocationRoleType}`.

### `src/views/admin/corpsec/my-tasks/table.js` (`Table`)

- **Chrome**: Section title (`CS in charge` / `CS Backup`), member `<select>`, company status filter (All + CMS statuses), striped HTML table.
- **Columns**: Company Name, Company Status, Transfer — maps **`props.companies`** to **`TaskRow`**.

### `src/views/admin/corpsec/my-tasks/taskRow.js` (`TaskRow`)

- **Company name**: Links to **`/admin/companies/edit/?cid={company._id}`**.
- **Status**: Resolves label from **`company.status`** against **`companyStatuses`**.
- **Transfer**: **`company.is_transfer`** → `"Yes"` / `"No"`.

### `src/components/admin-corpsec-side-sub-menu.js`

- **Nav**: **My Tasks** link to **`/admin/corpsec/my-tasks/`** when **`corpsec.my_tasks.enabled`** is true.
