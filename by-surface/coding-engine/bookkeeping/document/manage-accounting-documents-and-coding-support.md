# Manage accounting documents and coding support

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage accounting documents and coding support |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Bookkeeper, Finance User, Operations User |
| **Business Outcome** | Teams can capture, review, code, and reconcile accounting documents with consistent categories and amounts, using supplier context, conversion data, and past similar transactions. |
| **Entry Point / Surface** | Sleek App > Bookkeeping > Documents (receipts / invoices); API surface `document` (acct-coding-engine) |
| **Short Description** | Create and upload documents; list and retrieve details; update documents and payment status; bulk-delete eligible drafts; sync distinct supplier names; fetch conversion payloads for currency or date changes; load default line items when ML feedback and company rules allow; read invoice status from SleekBooks after publish; query similar historical transactions from BigQuery for consistent coding. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Sleek Receipts** (`SLEEK_RECEIPTS_URL` submit-receipt-v2) for multipart upload; **SleekBooks** (`sleekbooksService`) for journal entries / invoice details when checking publish eligibility and status; **Google BigQuery** (Dext inbox cost/sales tables) for similar-transaction lookup; **MongoDB** document store; **feedback** service for ML feedback and smart rules; **company** settings for accounting defaults; **user activity** and **sleek auditor** for audit trails on some paths; events published on bulk delete. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `documentdetailevents` (Document schema); related reads via company and feedback services as implemented |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `GET similar-transactions` requires `accountCrn` but `getSimilarTransactionForGivenAccountCrnAndSupplierName` only filters BigQuery by supplier/customer name and sales vs costs table—not obviously by account CRN; confirm intended behaviour. Exact in-app navigation labels may differ by product skin. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/document/document.controller.ts`

- **Auth surfaces**: Most user flows use `AuthGuard`; `ApiKeyGuard` on payment-status patch and supplier-category autopublish; `FrappeClientAuthGuard` on SB webhooks; `DocumentReExtractionGuard` with `AuthGuard` on bulk re-extract.
- **Similar transactions**: `GET document/similar-transactions` → `getSimilarTransactionForGivenAccountCrnAndSupplierName` (queries `accountCrn`, `supplier_or_customer_name`, `is_sales_invoice`).
- **CRUD / listing**: `POST document` (create, no `AuthGuard` on controller), `POST document/upload` (multipart, `AuthGuard`), `POST document/list` (`findAll` with user + auth token + app origin), `GET document/:documentId` (`getDocumentById`), `PUT document/:documentId` (`updateDocumentById`).
- **Coding support**: `POST document/conversion/:documentId` → `getDocumentConversionData`; `GET document/:documentId/default-line-items` → `getDefaultLineItem`.
- **Invoice status**: `GET document/:documentId/invoice-status` → `getDocumentInvoiceStatus`.
- **Supplier sync**: `GET document/supplier-sync` → `getDistinctSuppliers` (no `AuthGuard` on route—verify exposure).
- **Bulk delete**: `DELETE document/bulk-delete` → `bulkDelete` with `BulkDeleteDto` (max 50 ids per validation in service).

### `src/document/document.service.ts`

- **Upload**: Builds `FormData`, posts to `${SLEEK_RECEIPTS_URL}/api/document-events/submit-receipt-v2` with service authorization header.
- **Invoice status**: Loads document from MongoDB, inspects last `publish_entries` for SB publish; calls `sleekbooksService.getJournalEntry` or `getInvoiceDetailsFull`; derives eligibility vs `ENABLE_UPDATE_PUBLISHED_DOCUMENT` and invoice `status` / `docstatus`.
- **Distinct suppliers**: `documentModel.find(...).distinct('supplier', …)` with optional `createdAt` filter from query.
- **Default line items**: Only returns line items when status is `PROCESSING` or `ERROR`; uses `feedbackService.getFeedbackByDocumentId`, `companyModel` for `accounting_settings` / `ledger_type`, `getSpecificOrSmartRulesMapping`, `getLineItems`, GST helpers.
- **Conversion**: `getDocumentConversionData` loads document and calls `getAmountConvOnCurrOrDocDateChange` for amount/currency/date-driven conversion.
- **Similar transactions**: BigQuery job against `tb_dext_directload_inbox_costs` or `tb_dext_directload_inbox_sales` (location `asia-southeast1`), limit 10, ordered by `createdAt` DESC.
- **Bulk delete**: Validates ≤50 ids; only deletes documents in `EXTRACTING`, `PROCESSING`, or `ERROR`; `deleteMany`, duplicate cleanup, `DocumentEventType.BULK_DELETED`, audit logs.

### `src/document/models/document.schema.ts`

- MongoDB collection name: `documentdetailevents`.
