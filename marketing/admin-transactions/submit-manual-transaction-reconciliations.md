# Submit manual transaction reconciliations

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Submit manual transaction reconciliations |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal admin operators with **full** Sleek Business Account (`business_account`) permission — not users with edit-only permission |
| **Business Outcome** | When automated reconciliation cannot align platform and vendor-side movements, operators can batch record which SBA ledger rows and/or vendor references belong together, classify the situation, and leave an audit trail so downstream reporting and investigations stay consistent. |
| **Entry Point / Surface** | **sleek-website** admin: **`/admin/transactions/`** (webpack entry `admin/transactions`). **Business Account Transactions** page → toolbar button **Manual reconciliation** (visible only if `user.permissions.business_account === FULL`). `AdminLayout` with `sidebarActiveMenuItemKey="transactions"`. |
| **Short Description** | Dialog collects one or more entries: each row is **either** an SBA transaction Mongo `_id` **or** a vendor **ntryRef** plus vendor (DBS, CurrencyCloud, NIUM) — not both on the same row. Operators choose a **category** (preset list including internal adjustment, bank fee, vendor error, etc., or a custom label up to 100 characters) and **required remarks** (up to 500 characters). Multi-line paste expands rows for bulk SBA IDs or vendor refs. Submit calls the bank (SBA) admin API to create reconciliation records; on success the transaction list reloads. |
| **Variants / Markets** | **Unknown** in UI (SBA product is multi-region; no market gate in this dialog). |
| **Dependencies / Related Flows** | **`postManualReconciliation`** → **SBA API** `POST /sba/v2/admin/transactions/reconciliations` (base URL from `API_BANK_URL` or prod `https://sba-api.sleek.sg`). Same admin surface as listing/filtering transactions (`getTransactions` and related dialogs). Automated reconciliation and transaction detail chips (`is_reconcilable`, `reconciled_type`) are related but not implemented in these two files. **`createManualReconciliationEntries`** in `business-account-utils.js` wraps the same API for optional reuse. |
| **Service / Repository** | **sleek-website**: `src/views/admin/transactions/components/manual-reconciliation-dialog.js`, `src/utils/api-bank.js`. **SBA / bank backend** (sba-api): persistence and rules for reconciliation entries — not in this repo. |
| **DB - Collections** | **Unknown** (writes go through SBA API; Mongo or other stores not visible in sleek-website). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact backend validation (duplicate entries, idempotency, how entries merge with automated reconciliation). Whether **`createManualReconciliationEntries`** is used elsewhere in production or only the dialog path. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/transactions/index.js` (`TransactionList`)

- **`renderPrimaryToolbarContent`**: **Manual reconciliation** `Button` only when `sbaPermission === BUSINESS_ACCOUNT_PERMISSION.FULL` (not for `EDIT` alone). Opens `isManualReconciliationDialogOpen`.
- **`ManualReconciliationDialog`**: `onSuccess` → **`loadTransactions`** with current limit, page, filters, ordering.

### `src/views/admin/transactions/components/manual-reconciliation-dialog.js` (`ManualReconciliationDialog`)

- **`rowToEntry` / `isRowValid`**: each row must be exclusively SBA id **or** vendor ref + vendor; both filled is invalid.
- **`handlePasteSbaIds`** / **`handlePasteNtryRefs`**: multi-line clipboard splits into multiple rows.
- **`handleSubmit`**: payload **`{ entries, category, remarks }`** → **`postManualReconciliation`**. Errors from **`response.data.message`** or generic string.

### `src/utils/api-bank.js`

- **`getBaseUrl()`**: `API_BANK_URL`, else prod **`https://sba-api.sleek.sg`**, else **`http://localhost:4300`**.
- **`postManualReconciliation(body)`**: **`POST ${getBaseUrl()}/sba/v2/admin/transactions/reconciliations`** with JSON body via **`postResource`** / **`getDefaultHeaders()`** (session auth consistent with other admin bank calls).
