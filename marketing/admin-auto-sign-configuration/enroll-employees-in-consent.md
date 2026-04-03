# Enroll employees in consent

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Enroll employees in consent |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Lets CorpSec admins add users who belong to configured roles into the document-signing consent list so they can participate in automated document signing once enrolled. |
| **Entry Point / Surface** | Sleek Admin > Auto-Sign Configuration — **Add Employees** (`/admin/auto-sign-configuration/`, `AutoSignConfiguration`, sidebar key `auto-sign-configuration`; primary action opens `DialogV2` with `AddEmployeeDialog`) |
| **Short Description** | When CMS config enables `auto_sign_documents` and defines `add_employee_active_role_identifiers`, the page resolves matching groups via `getGroups`, loads members per group with `getAdminsByGroup`, and presents a grouped searchable multi-select. The admin checks employees and submits; the UI POSTs `user_id` per selection to `addNewUserToDocumentSigningConsent`, then refreshes the consent list. Requires `permissions.auto_sign_management` in `full` or `edit`. The Add action is hidden if no role identifiers are configured. |
| **Variants / Markets** | Unknown (gated by tenant CMS `incorp_transfer_workflow` / `auto_sign_documents`; not enumerated in this UI) |
| **Dependencies / Related Flows** | Same CMS allowlist and feature gate as [view roster](./view-auto-sign-consent-roster.md): `getPlatformConfig`, `getAppFeatureProp` for `add_employee_active_role_identifiers`; `api.getGroups`; roster refresh via `getAllConsents` after POST; toggling `auto_sign` after enrollment uses `updateUserDocumentSigningConsent` (separate confirmation flow in parent) |
| **Service / Repository** | `sleek-website` — `src/views/admin/auto-sign-configuration/index.js`, `src/views/admin/auto-sign-configuration/add-employee-dialog.js`; `src/utils/api.js` |
| **DB - Collections** | Unknown (consent rows created by API backing `POST /admin/document-signing-consent`, not defined in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/auto-sign-configuration/index.js`

- **Eligibility config:** `getCmsConfig` supplies `addEmployeeActiveRoleIdentifiersValue` from `incorp_transfer_workflow.props.auto_sign_documents.value.add_employee_active_role_identifiers` (lines 157–168). `fetchRoles` filters `api.getGroups()` to groups whose `identifier` is in that list (lines 132–136).
- **Add entry point:** `DataTable` receives `enableAddEmployeeAction={!!employeeActiveRoleIdentifiersValue.length}` and `onAddEmployees` (lines 230–234). `onAddEmployees` checks `hasPermissionToEdit` (`auto_sign_management` ∈ `full`/`edit`), sets dialog to `ACTION.BUTTON`, title “Add Employees”, primary “ADD EMAIL”, opens `DialogV2` (lines 301–311, 243–261).
- **Submit:** `onSubmitAddEmployees` dedupes checked rows, maps payloads to `{ user_id }`, and calls `api.addNewUserToDocumentSigningConsent` per payload via `Promise.all` (lines 347–368). On success, closes dialog and `fetchConsents()`; surfaces string error from response if present (lines 358–364).

### `src/views/admin/auto-sign-configuration/add-employee-dialog.js`

- **Population:** `useEffect` calls `fetchEmployees` when `activeRoles` changes (lines 73–75). `fetchEmployees` returns early if no roles (lines 85–86). For each `activeRole`, calls `api.getAdminsByGroup({ query: { group_id: group._id } })` and merges into grouped state (lines 84–111).
- **Selection UI:** Builds flat `employeeFilterValues` with `label`, `value` (`user._id`), `check`, `groups` (lines 114–124) and grouped `react-select` options (lines 126–136). Checkbox-style options toggle `check` and bubble via `onChangeMultipleSelectEmployees` to parent (lines 151–185, 172–185).
- **Primary button state:** Parent `addEmployeeDialog` disables primary until at least one employee has `check: true` (index.js lines 280–286).

### `src/utils/api.js`

- `addNewUserToDocumentSigningConsent`: `POST ${getBaseUrl()}/admin/document-signing-consent` (lines 2082–2085).
- `getAdminsByGroup`: `GET ${getBaseUrl()}/admin/users/admins` with `group_id` query (lines 335–337).
- `getGroups`: used by parent for role resolution (see `view-auto-sign-consent-roster.md` evidence).

### Navigation / bundle

- Webpack entry `admin/auto-sign-configuration` (`webpack/paths.js`); page title “Auto-Sign Configuration” (index.js lines 214–216).
