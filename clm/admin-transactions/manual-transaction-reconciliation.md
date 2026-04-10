# Manual Transaction Reconciliation

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manual Transaction Reconciliation |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (full permission only) |
| **Business Outcome** | Allows operations admins to resolve unmatched bank transactions by linking them to a categorised reconciliation entry with an audit trail of remarks, keeping the SBA ledger accurate and preventing unreconciled items from accumulating. |
| **Entry Point / Surface** | sleek-website Admin > Business Account Transactions > "Manual reconciliation" button (visible to FULL-permission admins only) |
| **Short Description** | Admins open a dialog from the Business Account Transactions page and submit one or more transaction references — either SBA internal IDs or vendor ntryRef + vendor name (DBS, CurrencyCloud, NIUM) — together with a reconciliation category and mandatory remarks. The form POSTs to the SBA reconciliations API, then refreshes the transaction list on success. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | SBA transaction list (admin-transactions index); upstream bank feeds from DBS, CurrencyCloud, NIUM; SBA backend `/sba/v2/admin/transactions/reconciliations` endpoint |
| **Service / Repository** | sleek-website (frontend); SBA backend service (inferred from `/sba/v2/` API path) |
| **DB - Collections** | Unknown (handled by SBA backend; collections not visible from frontend code) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which SBA backend service owns the `/sba/v2/admin/transactions/reconciliations` endpoint and what collections does it write to? 2. Is there an approval or audit workflow after submission, or is the reconciliation applied immediately? 3. Are there any market/jurisdiction restrictions (SG only, or HK/AU/UK too)? 4. The `HLB` category value appears alongside generic entries — is this a specific bank or a legacy label? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `src/views/admin/transactions/index.js` — "Manual reconciliation" button rendered at line ~351, gated by `sbaPermission === BUSINESS_ACCOUNT_PERMISSION.FULL`; opens `ManualReconciliationDialog` via `isManualReconciliationDialogOpen` state flag.

### Dialog component
- `src/views/admin/transactions/components/manual-reconciliation-dialog.js`
  - Accepts multiple rows; each row takes either an **SBA transaction `_id`** or a **vendor ntryRef + vendor name** (mutually exclusive per row, validated by `isRowValid()`).
  - Supports bulk-paste: pasting newline-delimited IDs into either field auto-expands rows.
  - **Vendors**: DBS, CurrencyCloud, NIUM.
  - **Categories**: `internal_adjustment`, `perfectly_offsetting`, `bank_fee`, `vendor_error`, `HLB`, `correction_entry`, plus a free-text custom category (max 100 chars).
  - **Remarks**: required, max 500 chars.
  - Payload shape: `{ entries: [{sba_transaction_id} | {vendor_transaction_id, vendor_name}], category, remarks }`.

### API call
- `src/utils/api-bank.js` — `postManualReconciliation(body)` → `POST /sba/v2/admin/transactions/reconciliations`.

### Permission gate
- `BUSINESS_ACCOUNT_PERMISSION.FULL` required (constant from `src/utils/constants`); users with EDIT permission see other transaction actions but not this button.
