# Persist consent mutations

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Persist consent mutations |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Ensures changes to the document-signing consent roster (adding users or toggling auto-sign) are written through the admin APIs and the on-screen list stays in sync with user-visible success or error feedback. |
| **Entry Point / Surface** | Sleek Admin > Auto-Sign Configuration (`/admin/auto-sign-configuration/`, `AutoSignConfiguration`, `sidebarActiveMenuItemKey` `auto-sign-configuration`) — **Add Employees** primary submit and **Confirm** on the auto-sign toggle dialogs |
| **Short Description** | After permission checks (`auto_sign_management` in `full` or `edit`), the page persists two kinds of change: (1) **Add employees** — `POST` per selected user via `addNewUserToDocumentSigningConsent` with `{ user_id }`, then closes the dialog, surfaces a string error from the API body if any, and calls `fetchConsents`. (2) **Toggle auto-sign** — `PUT` via `updateUserDocumentSigningConsent` with `{ auto_sign }`, mutates matching row in local `consents`, shows a Blueprint success toast, refetches, and shows error toasts on failure. Both paths refresh the list from `GET` `getAllConsents`. |
| **Variants / Markets** | Unknown (gated by tenant CMS `incorp_transfer_workflow` / `auto_sign_documents`; not enumerated in this UI) |
| **Dependencies / Related Flows** | UI entry and dialogs: [Enroll employees in consent](./enroll-employees-in-consent.md), [Toggle per-employee auto-sign](./toggle-per-employee-auto-sign.md); roster load [Fetch and format consent list](./fetch-and-format-consent-list.md); backend contract `POST`/`PUT` `/admin/document-signing-consent` (implementation outside this repo) |
| **Service / Repository** | `sleek-website` — `src/views/admin/auto-sign-configuration/index.js`, `src/utils/api.js` |
| **DB - Collections** | Unknown (persistence via APIs backing `/admin/document-signing-consent`, not defined in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/auto-sign-configuration/index.js`

- **List refresh:** `fetchConsents` calls `api.getAllConsents` with query (limit, offset, URL-derived filters), runs `consentsFormatter`, then `setConsents` / `setTotal` (lines 94–113). Invoked on mount, after add submit, after toggle success, and on filter change (lines 66–69, 364, 387, 403).
- **Add employees → API:** `onSubmitAddEmployees` dedupes checked `employeeFilterValues`, maps to `{ user_id }`, and `Promise.all` of `api.addNewUserToDocumentSigningConsent({ body: JSON.stringify(payload) })` (lines 347–356). On resolution: closes dialog; if any response item is a string, danger toast; else `fetchConsents()` (lines 358–364). Errors are only logged in `catch` (lines 366–368).
- **Toggle → API:** `updateDocumentSigningConsent` computes `toggled = !selectedEmployee.auto_sign`, calls `api.updateUserDocumentSigningConsent(selectedEmployee._id, { body: JSON.stringify({ auto_sign: toggled }) })` (lines 371–378). On success: updates `consent.auto_sign` in the in-memory `consents` array for the matching `_id`, success toast via `renderToastMessage` with `Intent.SUCCESS`, then `fetchConsents()` (lines 379–387). On error: danger toast with `error.message` (lines 389–390). `finally` closes the dialog (lines 392–394).
- **Toast helper:** `renderToastMessage` uses Blueprint `Toaster` / `Intent` with 3s timeout (lines 187–208).
- **Dialog routing:** `dialogOnClickPrimaryButton` dispatches `onSubmitAddEmployees` for `ACTION.BUTTON` and `updateDocumentSigningConsent` for `TOGGLE_ON` / `TOGGLE_OFF` (lines 331–340).

### `src/utils/api.js`

- `getAllConsents`: `GET ${getBaseUrl()}/admin/document-signing-consent` (lines 2077–2079).
- `addNewUserToDocumentSigningConsent`: `POST` same base path (lines 2082–2085).
- `updateUserDocumentSigningConsent(consentId, options)`: `PUT ${getBaseUrl()}/admin/document-signing-consent/${consentId}` (lines 2087–2090).
