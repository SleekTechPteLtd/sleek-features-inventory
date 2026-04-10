# Create and Edit Business Account Transactions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Create and Edit Business Account Transactions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (requires `business_account` permission: EDIT or FULL) |
| **Business Outcome** | Allows admins to manually inject or correct transaction records for a client's business account, ensuring the ledger reflects transfers that may not have been captured automatically. |
| **Entry Point / Surface** | Sleek Admin > Business Account Transactions > "CREATE TRANSACTION" button (create) or row action > Edit (update) |
| **Short Description** | A modal dialog that lets admins create a new transaction or edit an existing one on a client's SBA (Sleek Business Account). Required fields are company, currency account, direction (credit/debit), transfer type (local/international/charge), amount, and value date; optional fields include recipient/sender name, admin comment, and supporting document attachments (PDF/JPEG/PNG, max 5 MB each). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Browse & Search Business Account Transactions (list view); Inspect Transaction Record (detail view); SBA backend service (`/sba/v2/admin/…`); File storage service (folder creation + upload); `getCompanyBusinessAccounts` to populate currency-account dropdown |
| **Service / Repository** | sleek-website (frontend); SBA backend service (API owner, not in repo) |
| **DB - Collections** | Unknown (managed by SBA backend; likely a `transactions` collection — not visible from frontend code) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets/countries are supported — the virtual account number format suggests SG but the UI has no market gate; what permission level is required to edit an existing transaction vs create a new one (code shows EDIT or FULL for both); does the SBA backend emit any events (Kafka/webhooks) on transaction create/update? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/views/admin/transactions/components/add-transaction-dialog.js` — `NewTransactionDialog` React component; dual-mode (CREATE / UPDATE) controlled by `TRANSACTIONS_DIALOG_MODE` constant.
- `src/views/admin/transactions/index.js` — `TransactionList` page; hosts "CREATE TRANSACTION" toolbar button (visible to EDIT + FULL permissions), wires dialog open/close, and calls `onCloseDialogUpdateSuccess` to refresh the row after a successful edit.
- `src/utils/business-account-utils.js` — `createNewTransactionRequest`, `updateTransactionRequest`, `getCompanyBusinessAccounts` wrappers.
- `src/utils/api-bank.js` — raw HTTP calls: `POST /sba/v2/admin/transactions/request` (create), `PUT /sba/v2/admin/transactions/{id}/request` (update), `GET /sba/v2/admin/business-accounts` (currency account lookup).
- `src/views/admin/transactions/components/transaction-attachment-utils.js` — `createAttachmentFolder`, `uploadAllFiles`; stores files under `/companies/{company_id}/business_account/transaction_attachments/{timestamp}/`.

### Form fields
| Field | Required | Notes |
|---|---|---|
| Company | Yes | `NewCompanyLookup` component; sets `company_id` and `root_folder` |
| Currency Account | Yes | Populated from primary business account's `currency_accounts`; shows virtual account number + currency code |
| Value Date | No (defaults to today) | Constrained to [account created date, today] |
| Recipient / Sender | No | Stored as `origin.name` (credit) or `target.name` (debit) |
| Transfer Type | Yes | `local`, `international`, `charge` |
| Vendor | No (read-only) | Derived from selected currency account |
| Direction | Yes | `credit` or `debit` |
| Amount | Yes | Numeric, max 13 digits + 2 decimal places, must be > 0 |
| Currency | No (read-only) | Derived from selected currency account |
| Comment | No | Stored in `admin_actions.comment` |
| Attachments | No | PDF/JPEG/PNG, max 5 MB each; stored in `admin_actions.attachments` as `[{name, _id}]` |

### Permission guard
`getUser()` in `TransactionList` checks `user.permissions.business_account`; redirects to `/admin` if not READ/EDIT/FULL. The Create Transaction button and Edit action are only rendered for EDIT or FULL permission levels.
