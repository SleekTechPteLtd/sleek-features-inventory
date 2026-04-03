# Resolve active roles from groups

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Resolve active roles from groups |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Keeps role filters and the add-employee flow aligned with CMS policy by only exposing groups whose identifiers appear in `add_employee_active_role_identifiers`, instead of every group returned by the admin API. |
| **Entry Point / Surface** | Sleek Admin > Auto-Sign Configuration — `/admin/auto-sign-configuration/` (`AutoSignConfiguration`, sidebar key `auto-sign-configuration`); runs when the page loads after CMS config resolves the allowlist. |
| **Short Description** | Reads `add_employee_active_role_identifiers` from platform/CMS config (`incorp_transfer_workflow` → `auto_sign_documents`), then calls `GET /admin/groups` via `api.getGroups()` and filters groups to those whose `identifier` is in that list. The resulting `activeRoles` array powers the role column filter and is passed into `AddEmployeeDialog` for per-group employee loading. |
| **Variants / Markets** | Unknown (allowlist comes from tenant CMS; not enumerated in this UI) |
| **Dependencies / Related Flows** | `getPlatformConfig` / `getAppFeatureProp` / `getCmsConfig` supplies the identifier list; same identifiers drive `consentsFormatter` (user group → `roles` on each consent row). Consumers: `DataTable` (`activeRoles` for filter options), `AddEmployeeDialog` (`activeRoles` for `getAdminsByGroup` per `group._id`). Upstream API: `getGroups`. |
| **Service / Repository** | `sleek-website` — `src/views/admin/auto-sign-configuration/index.js`, `src/utils/api.js` |
| **DB - Collections** | Unknown (groups loaded via REST; persistence not in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/auto-sign-configuration/index.js`

- **Config → allowlist:** `initializeConfig` → `getCmsConfig` sets `employeeActiveRoleIdentifiersValue` from `add_employee_active_role_identifiers` under `auto_sign_documents.value` (lines 84–91, 157–167).
- **Fetch when allowlist non-empty:** `useEffect` depends on `employeeActiveRoleIdentifiersValue`; when length > 0, `fetchRoles` runs (lines 72–76).
- **Resolve active roles:** `fetchRoles` awaits `api.getGroups()`, filters `allGroups` with `employeeActiveRoleIdentifiersValue.includes(group.identifier)`, and `setActiveRoles` with the filtered list (lines 132–135).
- **Downstream props:** `activeRoles` passed to `DataTable` (role filter) and `AddEmployeeDialog` (lines 225–231, 288).

### `src/utils/api.js`

- **`getGroups`:** `GET ${getBaseUrl()}/admin/groups` via `getResource` (lines 1655–1657).

### Related consumers (not in feature file list)

- `src/views/admin/auto-sign-configuration/table.js` — `generateHeadRows` / `getOptions` map `activeRoles` to role filter options (`label: role.name`, `value: role._id`).
- `src/views/admin/auto-sign-configuration/add-employee-dialog.js` — iterates `activeRoles` to call `getAdminsByGroup` with each `group._id`.
