# Edit permission and verification gate

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Edit permission and verification gate |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Restricts who can change auto-sign configuration to users with the right CorpSec permission, and keeps unverified accounts from using the page until email verification completes. |
| **Entry Point / Surface** | Sleek Admin > Auto-Sign Configuration — `/admin/auto-sign-configuration/` (`AutoSignConfiguration`, sidebar key `auto-sign-configuration`); gates apply on initial session load and before add/toggle mutations. |
| **Short Description** | After `api.getUser()`, if `registered_at` is missing the browser is sent to `/verify/`. Edit capability is `hasPermissionToEdit` when `userResponse.permissions.auto_sign_management` is `full` or `edit`; without it, “Add employees” and auto-sign toggles show a danger toast and do not open mutation flows. If `getUser` fails, `checkResponseIfAuthorized` clears client storage and redirects to `/?redirect=…` on unauthorized responses. |
| **Variants / Markets** | Unknown (same tenant/session model as rest of admin; not enumerated in this UI) |
| **Dependencies / Related Flows** | `api.getUser` session; `addNewUserToDocumentSigningConsent` / `updateUserDocumentSigningConsent` (mutations guarded by `hasPermissionToEdit`); related roster view in same page (`view-auto-sign-consent-roster`) |
| **Service / Repository** | `sleek-website` — `src/views/admin/auto-sign-configuration/index.js`, `src/utils/auth-utils.js` |
| **DB - Collections** | Unknown (user and permissions come from API responses; not defined in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/auto-sign-configuration/index.js`

- **Email verification gate:** `fetchUser` calls `api.getUser()`, sets `emailVerified` from `registered_at != null`; when false, sets `window.location = "/verify/"` and returns (lines 115–122).
- **Edit permission:** `setPermissionToEdit(["full", "edit"].includes(userResponse.permissions.auto_sign_management))` (lines 124–125).
- **Mutation guards:** `onAddEmployees` and `onToggleSignature` both return early with `renderToastMessage(..., "toast-danger")` when `!hasPermissionToEdit`, citing CorpSec Admin (lines 301–317).
- **Unauthorized handling:** `fetchUser` `catch` passes `error.message` to `checkResponseIfAuthorized` (lines 126–129).
- **Render gate:** Page body renders only when `user` is set (`user && <AdminLayout …>`), so redirect or failed auth prevents showing the layout (lines 426–437).

### `src/utils/auth-utils.js`

- **`checkResponseIfAuthorized(responseStatus)`:** If `responseStatus` equals `HTTP_UNAUTHORIZED` (numeric or string from `./constants`), clears `store` and navigates to `/?redirect=${pathname+search}` (lines 12–16).

### Constants

- `HTTP_STATUS_CODES` / `HTTP_STATUSES` imported from `./constants` (auth-utils line 2); exact numeric values not duplicated here — see `src/utils/constants` if needed for parity with API errors.
