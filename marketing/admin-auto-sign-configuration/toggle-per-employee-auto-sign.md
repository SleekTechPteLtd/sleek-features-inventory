# Toggle per-employee auto-sign

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Toggle per-employee auto-sign |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Lets an authorized admin switch each document-signing consent row between automated and manual signing after explicit confirmation, so CorpSec can align signing behavior with policy per employee. |
| **Entry Point / Surface** | Sleek Admin > Auto-Sign Configuration — `/admin/auto-sign-configuration/` — per-row Material-UI `Switch` on the consent table (`sidebarActiveMenuItemKey` `auto-sign-configuration`) |
| **Short Description** | When CMS `auto_sign_documents` is enabled and the viewer has `permissions.auto_sign_management` in `full` or `edit`, toggling the row switch opens `DialogV2` with copy explaining automated vs manual signing for that employee. On **Confirm**, the client sends `PUT /admin/document-signing-consent/:id` with `{ auto_sign: toggled }` via `api.updateUserDocumentSigningConsent`, updates local state, shows a success toast, and refetches the roster. Users without edit permission get an error toast and no dialog commit. |
| **Variants / Markets** | Unknown (tenant CMS `incorp_transfer_workflow` / `auto_sign_documents`; not enumerated in this UI) |
| **Dependencies / Related Flows** | Same page as roster view: `getPlatformConfig` gates the table; `fetchConsents` / `getAllConsents` supplies rows; `updateDocumentSigningConsent` pairs with `addNewUserToDocumentSigningConsent` for adding employees; downstream document signing behavior lives in services behind the admin API (not in this repo) |
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

### `src/views/admin/auto-sign-configuration/table.js`

- **Control:** `Row` renders a Material-UI `Switch` with `checked={auto_sign}` and `onChange={() => props.onToggleSignature(row, !auto_sign)}` (lines 59–61), wiring each consent row to the parent toggle handler.

### `src/views/admin/auto-sign-configuration/index.js`

- **Permission:** `onToggleSignature` returns early with a danger toast if `!hasPermissionToEdit` (`userResponse.permissions.auto_sign_management` not in `full` or `edit`) (lines 313–316).
- **Dialog:** Sets `selectedEmployee`, derives `ACTION.TOGGLE_ON` vs `TOGGLE_OFF` from `!consent.auto_sign`, titles `CONFIRM_AUTOMATED_SIGNATURES` / `REMOVE_AUTOMATED_SIGNATURES`, body copy for automated vs manual signing (lines 313–328, 291–299).
- **Persist:** `updateDocumentSigningConsent` computes `toggled = !selectedEmployee.auto_sign`, calls `api.updateUserDocumentSigningConsent(selectedEmployee._id, { body: JSON.stringify({ auto_sign: toggled }) })`, patches matching row in `consents`, success toast, `fetchConsents()`, closes dialog in `finally` (lines 371–395).

### `src/utils/api.js`

- `updateUserDocumentSigningConsent(consentId, options)` → `PUT ${getBaseUrl()}/admin/document-signing-consent/${consentId}` (lines 2087–2089).
