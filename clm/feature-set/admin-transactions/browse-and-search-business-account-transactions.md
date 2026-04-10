# Browse and Search Business Account Transactions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Browse and Search Business Account Transactions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Ops Admin |
| **Business Outcome** | Gives ops admins a filterable, paginated view of the full transaction ledger so they can locate, review, and act on any business account transaction without needing direct database access. |
| **Entry Point / Surface** | Sleek Admin > Business Account > Transactions (`/admin/transactions`) |
| **Short Description** | Displays all SBA transactions in a paginated table. Admins can filter by transaction status, ops/admin status, compliance status, vendor (DBS, NIUM, CURRENCYCLOUD), date range, amount, currency, account number, company, transaction type, and sender/receiver name. Clicking a row opens the full transaction details dialog. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Transaction Details dialog (`details-transaction-dialog`); Create/Edit Transaction dialog (`add-transaction-dialog`); Manual Reconciliation dialog (`manual-reconciliation-dialog`); Company Select component; `TransactionActionsProvider` context; `TransactionUrlManager` (deep-link URL state); Business Account API (`/sba/v2`) |
| **Service / Repository** | sleek-website (frontend); Business Account Service (`sba/v2` — separate backend repo) |
| **DB - Collections** | Unknown (backend not in this repo; managed by Business Account Service) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets/regions are live for SBA (SG only, or also HK/UK/AU)? What backend service owns `/sba/v2/admin/transactions/all`? Are compliance_statuses a separate dimension from admin_statuses in the DB schema? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/views/admin/transactions/index.js` — `TransactionList` React class component; orchestrates state, filter logic, pagination, and dialog rendering
- `src/views/admin/transactions/components/new-table.js` — `NewTable` component; renders the table with inline column filters

### API endpoint
- `GET /sba/v2/admin/transactions/all` — fetches paginated transaction list; called via `apiBank.getTransactions()` in `src/utils/api-bank.js:184`
- Wrapped by `bankApi.getTransactions()` in `src/utils/business-account-utils.js:128`

### Query parameters sent to API
| Filter | Query param |
|---|---|
| Transaction Status | `statuses` |
| Admin/Ops Status | `admin_statuses` |
| Compliance Status | `compliance_statuses` |
| Vendor | `vendor` |
| Date range | `start_date`, `end_date` |
| Transaction ID | `transaction_id` |
| Sender/Receiver | `origin_target_name` |
| Transaction Type | `transaction_type` |
| Currency | `currency` |
| Amount | `amount` |
| Account Number | `account_number` |
| Company | `company_id` |
| Pagination | `limit`, `page` |

### Permission guard
- Requires `user.permissions.business_account` to be one of `read`, `edit`, or `full` (`BUSINESS_ACCOUNT_PERMISSION` constant, `src/utils/constants.js:2032`)
- `FULL` permission additionally shows the Manual Reconciliation button and Create Transaction button
- `EDIT` permission shows the Create Transaction button only

### Table columns (from `TRANSACTIONS_TABLE_HEADERS`, `src/utils/constants.js:2056`)
Transaction ID, Transaction Date, Company Name, Sender/Receiver, Account Number, Transaction Type/Source, Currency, Amount, Vendor, Transaction Status, Ops Status, Actions

### Status enumerations (`src/utils/constants.js:2080`)
- **Transaction Status**: `processing`, `approved`, `refunded`, `declined`, `deleted`, `new`, `incomplete`, `duplicated`
- **Admin/Ops Status**: `pending_update`, `pending_approval`, `canceled`, `approved`, `rejected`
- **Vendors**: `DBS`, `NIUM`, `CURRENCYCLOUD`

### URL deep-linking
- `TransactionUrlManager` (`src/views/admin/transactions/utils/transaction-url-manager.js`) allows linking directly to a transaction detail popup via URL params on page load

### Companion dialogs rendered on this page
- `DetailsTransactionDialog` — transaction detail view
- `NewTransactionDialog` — create / edit transaction (mode-driven)
- `ManualReconciliationDialog` — manual reconciliation (FULL permission only)
- File preview `Overlay` for transaction attachments
