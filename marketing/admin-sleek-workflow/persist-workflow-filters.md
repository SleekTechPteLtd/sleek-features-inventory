# Persist workflow filters

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Persist workflow filters |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (staff using Sleek Camunda workflow admin) |
| **Business Outcome** | Staff can return to the workflow list without re-applying company, status, and workflow-type filters when they use the navigation path that preserves filter state. |
| **Entry Point / Surface** | **sleek-website** admin: **Workflow** list at `/admin/sleek-workflow/` — `WorkFlowList` in `src/views/admin/sleek-workflow/index.js`; sidebar key `camunda-workflow` on `AdminLayout`. |
| **Short Description** | Persists filter control values (company, workflow status, workflow type) in `localStorage` under `workflowFilter` as JSON. When the user returns from a workflow task/detail view with `fromFilterDetails` set, `getFilterDefaultValue` reads that snapshot and updates list state. `componentCleanup` clears `workflowFilter` on unload unless `fromFilterDetails` is present, and always clears `fromFilterDetails`. The workflow task view sets `fromFilterDetails` when the user follows the “Workflow list” breadcrumb that calls `setFilterValue` before navigation; task mount also removes `fromFilterDetails` on load. Date range is applied to the API query string when set but is **not** included in the persisted JSON object. |
| **Variants / Markets** | Multi-tenant site (`getPlatformConfig` → `tenant` on list); filter behavior is not market-gated in this file. **SG, HK, UK, AU** typical for Sleek tenants — **Unknown** for exact parity across markets. |
| **Dependencies / Related Flows** | **sleek-website** `workflow-task/index.js`: `setFilterValue` (`localStorage` `fromFilterDetails`), `componentCleanup` on task view, breadcrumb href `CAMUNDA_WORKFLOW_CONSTANTS.PAGE_URLS.WORKFLOW_LIST` (`/admin/sleek-workflow/`). List APIs: `getSleekWorkflowProcesses` / `initialize`; filters built in `handleFilterChange`. **Filter** UI: `./components/filter`. **Companies** dropdown: `api.getCompanies`. |
| **Service / Repository** | **sleek-website**: `src/views/admin/sleek-workflow/index.js`, `src/views/admin/sleek-workflow/workflow-task/index.js`, `src/views/admin/sleek-workflow/constants/camunda-workflow-constants.js`. No server persistence for filter state — browser **localStorage** only. |
| **DB - Collections** | **None** for this feature (client-side `localStorage` only). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `getFilterDefaultValue` calls `this.handleFilterChange(defaultFilterValues)` with one argument, while `handleFilterChange` is defined as `(fieldName, data)` for a single control — restoration may not match intended behavior; worth verifying in browser. Task view `getFilterString` reads `tasksStatus` / `flowClass` from `workflowFilter`, while the list saves `workflowStatus` / `workflowType` — possible mismatch for any UI that relied on the task helper. Two “Workflow list” breadcrumb variants exist on the task page (`workflow-task/index.js` ~213 vs ~219); only the one with `onClick={setFilterValue}` sets `fromFilterDetails`. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-website — `src/views/admin/sleek-workflow/index.js`

- **Keys**: `workflowFilter` — JSON string `{ companyName, workflowStatus, workflowType }` (see `handleFilterChange`, `clearFilter`); `fromFilterDetails` — set when any of those three is active (`getFilterString`) and used on mount to decide whether to restore (`componentDidMount`).
- **Save on filter change**: `handleFilterChange` builds query segments (`backend_company_id`, `status`, `workflow_type`, optional `created_from` / `created_to` from `dateRange`), writes `workflowFilter` to `localStorage`, calls `getFilterString`, resets offset, calls `initialize`.
- **Restore**: `componentDidMount` reads `fromFilterDetails`; if absent, runs `initialize` without saved filter; then `getFilterDefaultValue(fromFilter)` parses `workflowFilter` when `fromFilter` is truthy.
- **Cleanup**: `componentCleanup` (beforeunload + `componentWillUnmount`): if `fromFilterDetails` is not set, removes `workflowFilter`; always removes `fromFilterDetails`.
- **Clear**: `clearFilter` resets `defaultFilterValues`, writes cleared object to `workflowFilter`, `initialize` with empty filter.

### sleek-website — `src/views/admin/sleek-workflow/workflow-task/index.js`

- **Return path**: `setFilterValue` does `localStorage.setItem("fromFilterDetails", true)` before following `href` to the workflow list (`CAMUNDA_WORKFLOW_CONSTANTS.PAGE_URLS.WORKFLOW_LIST`).
- **On task load**: `componentDidMount` removes `fromFilterDetails` (`localStorage.removeItem("fromFilterDetails")`) after init — so the flag for restore is expected to be set again only when leaving via `setFilterValue` (or equivalent), not when merely landing on the task page.
- **Task `componentCleanup`**: If `fromFilterDetails` is absent, removes `workflowFilter` (mirrors list cleanup semantics on unload).

### sleek-website — `src/views/admin/sleek-workflow/constants/camunda-workflow-constants.js`

- `PAGE_URLS.WORKFLOW_LIST`: `/admin/sleek-workflow/`.
