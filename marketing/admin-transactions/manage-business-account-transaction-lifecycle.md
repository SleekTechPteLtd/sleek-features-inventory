# Manage business account transaction lifecycle

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage business account transaction lifecycle |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal operators (Sleek Admin users with `permissions.business_account`: READ, EDIT, or FULL) |
| **Business Outcome** | Staff can list, filter, create, and correct business account payment requests; open shareable detail views; review attachments; and progress or stop requests (approve, reject, cancel, revert) within permission limits so outbound/inbound payment data stays accurate and traceable. |
| **Entry Point / Surface** | **sleek-website** admin: **Business Account Transactions** — `/admin/transactions/` (webpack entry `admin/transactions`; `AdminLayout` `sidebarActiveMenuItemKey="transactions"`). Deep links: `?transaction_id=<id>&isShowDetailPopup=true` opens the details dialog after load. |
| **Short Description** | Paginated transaction table with rich filters (statuses, ops/compliance, vendor, dates, company, amounts, etc.). Users with EDIT/FULL create or edit transactions via a dialog (company, currency account, direction, transfer type, value date, amount, comments, PDF/image attachments uploaded via company file folders). Details open in a tabbed dialog (details, conditional manual patch, outbound review for debits, related transactions for CARD/NIUM_PAYOUT) with attachment preview in an iframe overlay. `TransactionUrlManager` syncs `transaction_id` / `isShowDetailPopup` with `history.replaceState`. Manual patch actions (approve, reject, revert, cancel with comment) run through `TransactionActionsProvider` and REST wrappers in `business-account-utils` → `api-bank` SBA v2 admin transaction endpoints. |
| **Variants / Markets** | Unknown (tenant not specialized in these view files; SBA backend may vary by market). |
| **Dependencies / Related Flows** | **`api.getUser`** (email verification gate; `permissions.business_account`). **`bankApi.getTransactions`**, **`createNewTransactionRequest`**, **`updateTransactionRequest`**, **`cancelTransactionRequest`**, **`rejectTransactionRequest`**, **`approveTransactionRequest`**, **`revertTransactionRequest`**, **`patchTransaction`**, **`updateOutboundReviewRequest`**, **`getRelatedTransactions`** via **`utils/api-bank.js`** → bank/SBA API (`/sba/v2/admin/transactions/...`). **`getCompany`**, **`getCompanyBusinessAccounts`** for account/currency selection. **`getPreviewUrl`** / **`transaction-attachment-utils`** for file preview. Related: manual reconciliation dialog (FULL only), company lookup, outbound review and compliance flows (backend). |
| **Service / Repository** | **sleek-website**: `src/views/admin/transactions/index.js`, `.../components/add-transaction-dialog.js`, `.../components/details-transaction-dialog.js`, `.../utils/transaction-url-manager.js`, `src/utils/business-account-utils.js`, `src/utils/api-bank.js`. **Bank / SBA API** (external): admin transaction REST surface. |
| **DB - Collections** | Unknown — persistence is in the bank/SBA backend; **sleek-website** does not reference MongoDB collections for this feature. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `TransactionList.cancelTransaction` / `rejectTransaction` in `index.js` appear unused (actions are handled via `transaction-actions-context` and `manual-patch-tab.js`); confirm whether those list-level methods are dead code or reserved for a future wiring. Exact backend collections and audit trail storage for SBA transactions. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/transactions/index.js` (`TransactionList`)

- **Access**: `getUser()` → unverified users to `/verify/`; requires `BUSINESS_ACCOUNT_PERMISSION` **READ**, **EDIT**, or **FULL**; else redirect `/admin`.
- **Data**: `loadTransactions` → `bankApi.getTransactions({ query: { limit, page, ...filters } })`; state holds `transactionList`, `total`, pagination.
- **Deep link**: `TransactionUrlManager` — if `transaction_id` in URL and `isShowDetailPopup=true`, fetches that transaction and opens details; otherwise initial `loadTransactions`. On row detail open, `updateUrlForDialog(transaction_id)`; on close, `clearUrlForDialog()`.
- **Toolbar**: Title “Business Account Transactions”. **CREATE TRANSACTION** and **Manual reconciliation** (FULL only for reconciliation) shown only for **EDIT** or **FULL**.
- **Dialogs**: `NewTransactionDialog` (create/update modes); `DetailsTransactionDialog` wrapped in `TransactionActionsProvider`; `ManualReconciliationDialog` for FULL. **`onClickPreviewFile`** → `getPreviewUrl(fileId)` → Blueprint `Overlay` + `iframe` preview.
- **Helpers**: `cancelTransaction` / `rejectTransaction` call `bankApi.cancelTransactionRequest` / `rejectTransactionRequest` and refresh list item — **not referenced** from JSX in this file (see open question).

### `src/views/admin/transactions/components/add-transaction-dialog.js` (`NewTransactionDialog`)

- **Create/update**: `createNewTransactionRequest` / `updateTransactionRequest` from `business-account-utils`; payload includes `company_id`, `currency_account_id`, `amount`, `direction`, `valueDate`, `transfer_type`, optional `origin.name` / `target.name`, `admin_actions.comment` and attachment refs.
- **Data loading**: `getCompanyBusinessAccounts`, `getCompany` for `root_folder`; `createAttachmentFolder` + `uploadAllFiles` for new files (PDF/JPEG/PNG, max 5MB).
- **UI**: Company lookup, currency account select, value date bounds vs account creation, transfer type (local/international/charge), direction credit/debit, amount validation.

### `src/views/admin/transactions/components/details-transaction-dialog.js`

- **Tabs**: Details always; **Manual Patch** if `admin_actions.admin_status` set and user has EDIT/FULL; **Outbound Review** if `direction === "debit"`; **Related Transactions** if `product_category` in `CARD`, `NIUM_PAYOUT`. **Patch** affordance in details gated by FULL (`showPatchButton`).
- Delegates to `DetailsTab`, `ManualPatchTab`, `OutboundReviewTab`, `RelatedTransactionsTab`.

### `src/views/admin/transactions/utils/transaction-url-manager.js` (`TransactionUrlManager`)

- Query params: `transaction_id`, `isShowDetailPopup`; `replaceState` on open/close; `openNewTabForTransaction` for new-tab deep links.

### `src/utils/business-account-utils.js`

- Transaction API: `getTransactions`, `getRelatedTransactions`, `createNewTransactionRequest`, `updateTransactionRequest`, `patchTransaction`, `approveTransactionRequest`, `rejectTransactionRequest`, `cancelTransactionRequest`, `revertTransactionRequest`, `updateOutboundReviewRequest` — each delegates to `api-bank` with JSON bodies where required.

### `src/utils/api-bank.js` (SBA v2 admin paths)

- Examples: `GET .../sba/v2/admin/transactions/all`, `POST .../transactions/request`, `PUT .../transactions/{_id}/request`, `POST .../approve`, `.../reject`, `.../cancel` (with body), `.../revert`, `.../patch`, related-transactions endpoint.

### `src/views/admin/transactions/contexts/transaction-actions-context.js`

- **`TransactionActionsProvider`**: wires `approveTransactionRequest`, `rejectTransactionRequest`, `revertTransactionRequest`, `cancelTransactionRequest` (with `{ comment }`), `updateOutboundReviewRequest`; updates local transaction and notifies parent `onTransactionUpdated`.

### `src/views/admin/transactions/components/manual-patch-tab.js`

- Uses `useTransactionActions()` for approve / reject / revert / cancel with confirmation dialogs; attachment download/preview hooks; edit transaction opens parent callback.
