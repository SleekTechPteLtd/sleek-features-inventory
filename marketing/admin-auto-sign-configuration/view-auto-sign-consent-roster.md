# View auto-sign consent roster

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | View auto-sign consent roster |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Gives CorpSec and operations a single place to see which employees are in scope for auto-sign, their roles, and whether each person’s documents are set to auto or manual signing when the product feature is turned on. |
| **Entry Point / Surface** | Sleek Admin > Auto-Sign Configuration — `/admin/auto-sign-configuration/` (`AutoSignConfiguration`, sidebar key `auto-sign-configuration`) |
| **Short Description** | When CMS platform config enables `auto_sign_documents` under `incorp_transfer_workflow`, the page loads consent rows from `GET /admin/document-signing-consent` and maps each user’s groups to a `roles` list filtered by `add_employee_active_role_identifiers`. The table shows name, email, role names, and a toggle for `auto_sign`. Multi-select filters (employee, role, automated vs manual) update the URL query string and refetch. If the feature flag is off, the body shows “This feature is disabled.” Editing add/toggle actions requires `permissions.auto_sign_management` in `full` or `edit`. |
| **Variants / Markets** | Unknown (gated by tenant CMS `incorp_transfer_workflow` / `auto_sign_documents`; not enumerated in this UI) |
| **Dependencies / Related Flows** | `getPlatformConfig` + `getAppFeatureProp` for feature gating and role allowlist; `api.getAllConsents` → `/admin/document-signing-consent`; `api.getGroups` → `/admin/groups` for role labels; `api.getUser` (unverified → `/verify/`); updates via `addNewUserToDocumentSigningConsent` / `updateUserDocumentSigningConsent` (same feature area, not required to view the roster) |
| **Service / Repository** | `sleek-website` — `src/views/admin/auto-sign-configuration/index.js`, `src/views/admin/auto-sign-configuration/table.js`; `src/utils/api.js` |
| **DB - Collections** | Unknown (consent records persisted by API backing `/admin/document-signing-consent`, not defined in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/auto-sign-configuration/index.js`

- **Mount:** `initializeConfig` (CMS auto-sign enabled + `add_employee_active_role_identifiers`), `fetchConsents`, `fetchUser` in `useEffect` (lines 66–70).
- **Feature gate:** `getCmsConfig` reads `platformConfig.cmsAppFeatures` → `incorp_transfer_workflow.props.auto_sign_documents` for `enabled` and `add_employee_active_role_identifiers` (lines 157–168, 84–91). When `isAutoSignDocumentsEnabled` is false, body renders “This feature is disabled.” instead of `DataTable` (lines 224–242).
- **Data:** `fetchConsents` calls `api.getAllConsents` with `limit`/`offset` and filters from `getDefaultFilter()` (query string: `userId`, `roleId`, `automatedSignature`) (lines 94–113, 138–155). `consentsFormatter` attaches `roles` from `consent.user.groups` intersected with `addEmployeeActiveRoleIdentifiersValue` (lines 170–185).
- **Auth:** `fetchUser` → `api.getUser()`; `hasPermissionToEdit` from `userResponse.permissions.auto_sign_management` ∈ `["full","edit"]` (lines 115–130, 124–125).
- **Table wiring:** `DataTable` receives `dataSource={consents}`, `activeRoles`, `enableFiltering`, `defaultValues`, `onAddEmployees`, `onToggleSignature`, `handleFilterChange` (lines 225–237).

### `src/views/admin/auto-sign-configuration/table.js`

- **Row:** `Row` renders `user.first_name` / `last_name`, `user.email`, `roles` names joined with `" / "`, and Material-UI `Switch` bound to `auto_sign` calling `onToggleSignature(row, !auto_sign)` (lines 39–62).
- **Filters:** `generateHeadRows` builds react-select filter columns for employee, role (`activeRoles`), and automated signature true/false; disabled when `enableFiltering` is false until consents load (lines 137–161, 318–319; parent sets `enableFiltering` when `consents.length` — index.js lines 78–82).

### `src/utils/api.js`

- `getAllConsents`: `GET ${getBaseUrl()}/admin/document-signing-consent` (lines 2077–2079).
- `getGroups`: `GET ${getBaseUrl()}/admin/groups` (lines 1655–1657).
- `updateUserDocumentSigningConsent` / `addNewUserToDocumentSigningConsent`: `PUT`/`POST` under `/admin/document-signing-consent` (lines 2082–2089).

### Navigation

- Webpack entry `admin/auto-sign-configuration`; sidebar link `href="/admin/auto-sign-configuration/"`, key `auto-sign-configuration` (`src/components/new-admin-side-menu.js`).
