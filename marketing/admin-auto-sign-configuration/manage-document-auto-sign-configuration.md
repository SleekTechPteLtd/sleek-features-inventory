# Manage document auto-sign configuration

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage document auto-sign configuration |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (authorized for auto-sign management) |
| **Business Outcome** | Lets CorpSec-aligned admins review who is enrolled in document-signing consent, narrow the roster by person, role, and signature mode, add eligible staff, and set each person to automated or manual signing so execution matches corporate policy. |
| **Entry Point / Surface** | Sleek Admin — **Auto-Sign Configuration** (`/admin/auto-sign-configuration/`), `sidebarActiveMenuItemKey` `auto-sign-configuration`, rendered via `AutoSignConfiguration` in `index.js` |
| **Short Description** | When tenant CMS `incorp_transfer_workflow` → `auto_sign_documents` is enabled, the page loads document-signing consents from the admin API, optionally restricts which roles appear and who can be added using configured group identifiers, and exposes filters (employee, role, auto vs manual), an **Add Employees** flow backed by group-scoped admin directory lookup, and per-row toggles with confirmation dialogs. Edits require `permissions.auto_sign_management` in `full` or `edit`; others see read-only behavior and error toasts. Unverified users are redirected to `/verify/`. |
| **Variants / Markets** | Unknown (driven by CMS `auto_sign_documents` and `add_employee_active_role_identifiers`; not hard-coded per market in this UI) |
| **Dependencies / Related Flows** | **Upstream:** `getPlatformConfig` / `getAppFeatureProp` for CMS feature flags; `api.getUser` for session and permission; `api.getGroups` + configured role identifiers for eligible roles; `api.getAdminsByGroup` to list staff per role for enrollment. **API:** `GET`/`POST`/`PUT` on `/admin/document-signing-consent` (and `GET /admin/users/admins`). **Downstream:** actual document routing and e-sign behavior live in services behind those admin routes (not implemented in this repo). |
| **Service / Repository** | `sleek-website` — `src/views/admin/auto-sign-configuration/index.js`, `src/views/admin/auto-sign-configuration/table.js`, `src/views/admin/auto-sign-configuration/add-employee-dialog.js`, `src/utils/api.js` |
| **DB - Collections** | Unknown (consent and user data persisted by the API backing `/admin/document-signing-consent`; no Mongo schemas in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/auto-sign-configuration/index.js`

- **Feature gate:** `getCmsConfig` reads `incorp_transfer_workflow.props.auto_sign_documents` for `enabled` and `add_employee_active_role_identifiers`; when disabled, body shows “This feature is disabled.”
- **Session:** `fetchUser` uses `api.getUser`; email verification gate to `/verify/`; `hasPermissionToEdit` from `["full", "edit"].includes(userResponse.permissions.auto_sign_management)`.
- **Data:** `fetchConsents` calls `api.getAllConsents` with query (`limit`, `offset`, plus URL-derived `userId`, `roleId`, `automatedSignature`); `consentsFormatter` attaches `roles` filtered to configured identifiers.
- **Actions:** `onAddEmployees` / `onSubmitAddEmployees` → `api.addNewUserToDocumentSigningConsent` per selected `user_id`; `updateDocumentSigningConsent` → `api.updateUserDocumentSigningConsent` with `{ auto_sign }`; `setPathName` syncs filters to the query string.

### `src/views/admin/auto-sign-configuration/table.js`

- **Filters:** `generateHeadRows` builds react-select filters for `userId`, `roleId`, `automatedSignature` (`true` / `false`); `handleFilterChange` updates parent and refetches.
- **Roster:** Each `Row` shows name, email, role names, and a `Switch` for `auto_sign` calling `onToggleSignature`.
- **Add:** **ADD EMPLOYEES** is disabled unless `enableAddEmployeeAction` (derived from configured role identifiers).

### `src/views/admin/auto-sign-configuration/add-employee-dialog.js`

- **Eligibility list:** For each `activeRoles` group, `api.getAdminsByGroup({ query: { group_id: group._id } })`; results grouped for multi-select with search; selection feeds parent payloads for `POST` consent enrollment.

### `src/utils/api.js`

- `getAdminsByGroup` → `GET ${getBaseUrl()}/admin/users/admins` (query e.g. `group_id`).
- `getAllConsents` → `GET ${getBaseUrl()}/admin/document-signing-consent`.
- `addNewUserToDocumentSigningConsent` → `POST ${getBaseUrl()}/admin/document-signing-consent`.
- `updateUserDocumentSigningConsent(consentId, …)` → `PUT ${getBaseUrl()}/admin/document-signing-consent/${consentId}`.
