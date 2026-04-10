# Inspect Transaction Record

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Inspect Transaction Record |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (Internal Operations / Compliance staff) |
| **Business Outcome** | Enables admins to investigate the full lifecycle and counterparty details of any transaction, including compliance status, manual patch history, outbound review, and related fund-flow steps — supporting operations, reconciliation, and compliance reviews. |
| **Entry Point / Surface** | Sleek Admin > Transactions > [Transaction row click] > Details dialog |
| **Short Description** | A tabbed modal dialog surfacing all structured data for a selected transaction. Always shows core fields (basic info, transfer details, origin/target parties, financial details, IDs, reconciliation flags). Conditionally renders a Manual Patch tab (admin with edit/full `business_account` permission and `admin_status` set), an Outbound Review tab (debit-direction transactions), and a Related Transactions tab (CARD and NIUM_PAYOUT product categories, showing the full RHA fund-flow chain). |
| **Variants / Markets** | Unknown (PayNow QR section is SG-specific; no explicit market gates in dialog logic) |
| **Dependencies / Related Flows** | Manual Patch tab (`ManualPatchTab`, `PatchTransactionDialog`); Outbound Review tab (`OutboundReviewTab`); RHA related-transactions lookup (`apiBank.getRelatedTransactions`); Transaction Status chip; `BUSINESS_ACCOUNT_PERMISSION` RBAC constants |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown (frontend only; backend collections not visible from these files) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which backend service/repo powers `apiBank.getRelatedTransactions` and what collections does it touch? What is the full enum of `product_category` values beyond CARD and NIUM_PAYOUT? Is `admin_status` set exclusively by ops/compliance workflows or also by automated rules? Is the PayNow QR section gated to SG only at the API level? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/views/admin/transactions/components/details-transaction-dialog.js` — top-level dialog container; tab visibility logic driven by `transaction.direction`, `transaction.product_category`, `transaction.admin_actions.admin_status`, and `user.permissions.business_account`
- `src/views/admin/transactions/components/details-tab.js` — main Details tab; renders seven sections: Transaction Summary, Basic Information, Transfer Details, Party Information, PayNow QR Details, Financial Details, Additional Details; exposes a Patch button for `FULL`-permission admins
- `src/views/admin/transactions/components/related-transactions-tab.js` — Related Transactions tab; calls `getRelatedTransactions(transaction._id)` → `apiBank.getRelatedTransactions({ query: { transactionId } })`; renders the original transaction and ordered RHA step transactions (collection debit/transfer/credit, refund debit/transfer/credit); deep-links each transaction ID to the admin transactions page

### Key fields displayed (Details tab)
- **Basic Info**: `company_name`, `account_number`, `transaction_date`, `valueDate`
- **Transfer Details**: `transfer_type`, `transaction_type`, `transaction_source`, `vendor`, `transaction_description`, `purpose_of_transfer`, `customer_reference`
- **Party Info**: `origin.name`, `origin.bank_account`, `origin.card_number`, `origin.bic_swift`, `target.name`, `target.proxy_type`, `target.proxy_value`, `target.bank_account`, `target.bic_swift`, bank country codes
- **PayNow QR**: `paynowQr.business_account_user.user_email`, `paynowQr.createdAt`, `paynowQr.paynow_data.purposeOfPayment`
- **Financial**: `amount`, `currency`, `destination_amount`, `destination_currency`, `forex_rate`
- **Additional**: `transaction_id`, `_id`, `transaction_ref`, `meta_data.entry_reference` / `meta_data.transactionId`, `status_description`, `is_reconcilable`, `is_hidden`, `reconciled_type[]`

### Permission model
- `BUSINESS_ACCOUNT_PERMISSION.READ` — can open the dialog
- `BUSINESS_ACCOUNT_PERMISSION.EDIT` or `FULL` + `admin_actions.admin_status` set → Manual Patch tab visible
- `BUSINESS_ACCOUNT_PERMISSION.FULL` → Patch button in Details tab visible
- `transaction.direction === "debit"` → Outbound Review tab visible
- `transaction.product_category` in `["CARD", "NIUM_PAYOUT"]` → Related Transactions tab visible

### RHA step types (Related Transactions tab)
`RHA_COLLECTION_DEBIT`, `RHA_COLLECTION_TRANSFER`, `RHA_COLLECTION_CREDIT`, `RHA_REFUND_COLLECTION_DEBIT`, `RHA_REFUND_COLLECTION_TRANSFER`, `RHA_REFUND_COLLECTION_CREDIT`

### External calls
- `apiBank.getRelatedTransactions` — fetches RHA-linked transactions by `transactionId`
