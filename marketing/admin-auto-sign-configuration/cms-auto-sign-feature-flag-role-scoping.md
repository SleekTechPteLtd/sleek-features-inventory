# Auto-sign CMS config gating

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Auto-sign CMS config gating |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Lets tenant CMS platform configuration turn the Auto-Sign Configuration admin surface on or off and restrict which group identifiers power “add employee” and which roles appear in each row, without a frontend deploy. |
| **Entry Point / Surface** | Sleek Admin > Auto-Sign Configuration — `/admin/auto-sign-configuration/`; config is applied on mount via `initializeConfig` / `getCmsConfig` in `AutoSignConfiguration` |
| **Short Description** | `getPlatformConfig()` (with optional `localStorage` cache keyed by build) supplies `cmsAppFeatures`. `getAppFeatureProp` walks `incorp_transfer_workflow` → nested `auto_sign_documents`: `enabled` gates the main table vs “This feature is disabled.” `value.add_employee_active_role_identifiers` limits which consent user groups become `roles` for row display and drives `fetchRoles` (intersection with `api.getGroups()`). The Add Employees button is shown only when that allowlist is non-empty. |
| **Variants / Markets** | Unknown (values come from CMS; not hard-coded per market in this code) |
| **Dependencies / Related Flows** | `getPlatformConfig` / `api.getPlatformConfig({ platform: "admin" })`; `getAppFeatureProp`; downstream: `fetchRoles`, `consentsFormatter`, `DataTable` props (`enableAddEmployeeAction`, `activeRoles`); related feature doc: view auto-sign consent roster |
| **Service / Repository** | `sleek-website` — `src/utils/config-loader.js`, `src/utils/app-feature-utils.js`, `src/views/admin/auto-sign-configuration/index.js` |
| **DB - Collections** | Unknown (platform config and CMS feature payloads are returned by the config API and cached client-side, not defined in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `config-loader.js` ends with `module.export` instead of `module.exports` for the CommonJS block — verify bundler treats exports as intended. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/utils/config-loader.js`

- **`getPlatformConfig`:** Returns parsed `localStorage.platformConfig` when present, non-empty, `BUILD_NUMBER` matches `lastKnownBuildVersion`, and build is not `development`; otherwise calls `api.getPlatformConfig({ platform: "admin" })`, persists JSON to `localStorage`, updates `lastKnownBuildVersion`, returns `platformConfig.data` (lines 9–26).

### `src/utils/app-feature-utils.js`

- **`getAppFeatureProp(props, appFeaturePropName)`:** Uses lodash `find` to return the object in `props` whose `name` matches `appFeaturePropName` (lines 1–5). Used to resolve nested CMS feature entries by name.

### `src/views/admin/auto-sign-configuration/index.js`

- **`getCmsConfig`:** Loads `platformConfig` via `getPlatformConfig()`, then `getAppFeatureProp(platformConfig.cmsAppFeatures, "incorp_transfer_workflow")`, then `getAppFeatureProp(incorpTransferWorkflow.props, "auto_sign_documents")`. Reads `enabled` → `isAutoSignDocumentsEnabled`, and `value.add_employee_active_role_identifiers` → `addEmployeeActiveRoleIdentifiersValue` (default `[]`) (lines 157–168).
- **`initializeConfig`:** Applies `isAutoSignDocumentsEnabled` to `isEnabled` and stores `addEmployeeActiveRoleIdentifiersValue` for downstream effects (lines 84–91).
- **`fetchRoles`:** When `employeeActiveRoleIdentifiersValue` is set, loads all groups via `api.getGroups()` and keeps those whose `identifier` is in the CMS allowlist (lines 132–136, 72–76).
- **`consentsFormatter`:** For each consent, filters `consent.user.groups` to identifiers in `addEmployeeActiveRoleIdentifiersValue` and exposes the result as `roles` for table display (lines 170–185). If the allowlist is empty, formatter returns data unchanged (no role subsetting).
- **UI gating:** `isEnabled` controls whether `DataTable` renders or the disabled message (lines 224–242). `enableAddEmployeeAction={!!employeeActiveRoleIdentifiersValue.length}` (line 230). `AddEmployeeDialog` receives `activeRoles` from the filtered groups list (lines 288, 225–231).

### `src/views/admin/auto-sign-configuration/table.js` (consumer)

- **Row display:** `Row` renders `roles` names from the prop produced by `consentsFormatter` (lines 39–58).
- **Add Employees:** `enableAddEmployeeAction` disables the ADD EMPLOYEES button when false (lines 323–324).

### `src/views/admin/auto-sign-configuration/add-employee-dialog.js` (consumer)

- **`activeRoles`:** Employee pick lists are built only from `activeRoles` (groups in the CMS allowlist); `fetchEmployees` no-ops when `activeRoles` is empty (lines 84–85, 71).
