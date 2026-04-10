# Review Manual Transaction Patch Requests

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Review Manual Transaction Patch Requests |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Ops Admin |
| **Business Outcome** | Ensures manual edits to business account transactions pass a two-eye approval check before taking effect, preventing unauthorised or erroneous financial changes from going live unreviewed. |
| **Entry Point / Surface** | Sleek Admin > Transactions > Manual Patch Tab (internal ops tool) |
| **Short Description** | Ops admins with `full` business_account permission review pending manual patch requests and can approve, reject, cancel, or revert them. Approved patches expose a time-limited revert window (`revertable_time`) visible in the UI. Admins with `edit` permission may only modify pending requests — not approve or reject. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Create Manual Patch Request (upstream); SBA Admin Transaction List; transaction attachment preview/download |
| **Service / Repository** | sleek-website (frontend); backend SBA service at `/sba/v2/admin/transactions` (repo unknown) |
| **DB - Collections** | Unknown (frontend only; backend collections not visible in source files) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | (1) What is the revert window duration — is it configured per-transaction at approval time or globally? (2) Is the two-eye rule enforced server-side (i.e. blocked if approver == requester)? (3) Which backend repo owns `/sba/v2/admin/transactions/:id/approve\|reject\|cancel\|revert`? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### UI component
`views/admin/transactions/components/manual-patch-tab.js`
- `ManualPatchTab` renders approve / reject / cancel / revert buttons conditionally based on `admin_status` and `BUSINESS_ACCOUNT_PERMISSION`.
- **Approve / Reject**: visible when `sbaPermission === "full"` AND `admin_status === "pending_approval"`.
- **Cancel**: visible when `sbaPermission === "full"` AND `admin_status` is `"pending_approval"` or `"pending_update"`.
- **Edit**: visible when `sbaPermission === "full"` or `"edit"` AND `admin_status` is `"pending_update"` or `"pending_approval"`.
- **Revert**: visible when `sbaPermission === "full"` AND `admin_status === "approved"` AND `now < revertable_time`.
- Each action opens a `ConfirmationDialog` before submission.
- Displays requester info (created_by / updated_by) and approver info (approved_by / rejected_by / canceled_by) with timestamps.
- Displays attachments (supporting documents) with download and preview actions.

### Context / state management
`views/admin/transactions/contexts/transaction-actions-context.js`
- `TransactionActionsProvider` holds `localTransaction` and `isSubmitting` state.
- Exposes: `onApproveManualPatch`, `onRejectManualPatch`, `onRevertManualPatch`, `onCancelManualPatch`.
- Calls `bankApi.*` from `utils/business-account-utils.js`, which proxies to `utils/api-bank.js`.

### API calls (`utils/api-bank.js`)
| Action | Method | Endpoint |
|---|---|---|
| Approve | `PUT` | `/sba/v2/admin/transactions/:id/approve` |
| Reject | `PUT` | `/sba/v2/admin/transactions/:id/reject` |
| Cancel | `PUT` | `/sba/v2/admin/transactions/:id/cancel` (body: `{ comment }`) |
| Revert | `PUT` | `/sba/v2/admin/transactions/:id/revert` |

### Admin status state machine (`utils/constants.js`)
```
pending_update → pending_approval → approved → (revert window) → reverted
                                 → rejected
              → canceled
pending_approval → canceled
```
Constants: `TRANSACTIONS_CONSTANTS.ADMIN_STATUS` — `pending_update`, `pending_approval`, `canceled`, `approved`, `rejected`.

### Permission model
`BUSINESS_ACCOUNT_PERMISSION`: `full` (approve/reject/cancel/revert/edit), `edit` (edit only), `read` (view only).
