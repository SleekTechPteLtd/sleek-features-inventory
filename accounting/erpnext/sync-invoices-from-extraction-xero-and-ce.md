# Sync invoices from extraction, Xero, and CE

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync invoices from extraction, Xero, and CE |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Purchase and sales documents from extraction pipelines, Xero migration, and the Coding Engine are represented consistently in SleekBooks (ERPNext), with attachments where needed, so finance teams can review payment, bank, and submission state in one ledger. |
| **Entry Point / Surface** | Backend integration: `sleek-erpnext-service` HTTP routes under `erpnext` (`ErpnextController`), plus event-driven creation from `CESleekBooksInvoiceCreatedEvent` (`InvoiceListener`). Not a single end-user screen; upstream services and jobs call these APIs or emit events. |
| **Short Description** | Creates and updates purchase and sales invoices (and related flows) in ERPNext via REST: lookup by extraction id, generic invoice save, Xero- and CE-sourced create/submit/amend paths, Dext download-and-attach, file upload, and read APIs that bundle invoice detail with payment entries and bank transactions. Submitted CE documents can be moved to draft, updated, and re-submitted. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream** — document extraction (extraction id on ERPNext docs); **Coding Engine** — `CESleekBooksInvoiceCreatedEvent` → `createPurchaseInvoiceFromCE` / `createSalesInvoiceFromCE`; **Xero** — `createPurchaseInvoiceFromXero`, `createSalesInvoiceFromXero`, `submitInvoiceFromXero`, `createPaymentFromXero`, related bank flows. **External** — ERPNext/Frappe (`ERPNEXTBASEURL`, `sleek.api.*` helpers). **Downstream** — `DataStreamerService` / CE invoice done-failed events from service where emitted; **Sleek Auditor** for audit hooks. **Related** — Dext/Hubdoc helpers in `ErpnextService` for attachment sync. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | None in this layer for these flows: `ErpnextService` does not inject Mongoose models; invoice documents are read and written through ERPNext HTTP APIs. (`ErpnextModule` registers `Companies` for other concerns; not used by the invoice methods cited.) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `GET /get-bulk-invoice-details-with-payment-entry-and-bank-transaction` uses a request body with `GetBulkInvoiceDetailsWithPaymentEntryAndBankTransactionDto` — some clients/stacks treat GET bodies as unreliable; is this intentional? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/erpnext/erpnext.controller.ts`

- **Extraction-linked reads**: `GET /get-invoice/:extractionId` → `getInvoiceByExtractionId`; `GET /get-invoices` → `getInvoices` (`GetInvoiceQueryDto` / `GetInvoicesQueryDto` with `docType`).
- **Generic create**: `POST /create-invoices` → `createInvoices` (Frappe `savedocs` payload).
- **Dext / files**: `POST /download-upload-dext-attachment` → `downloadAndUploadAttachment`; `POST /upload-invoice-file` → `uploadInvoiceFile`.
- **Detail + payment + bank**: `GET /get-invoice-details-with-payment-entry-and-bank-transaction` → `getInvoiceDetailsWithPaymentEntryAndBankTransaction`; `GET /get-bulk-invoice-details-with-payment-entry-and-bank-transaction` → `getBulkInvoiceDetailsWithPaymentEntryAndBankTransaction` (body: `invoiceIds`, `invoiceType`).
- **Purchase / sales reads**: `GET /get-purchase-invoice`, `/get-purchase-invoice-full`, `/get-sales-invoice`, `/get-sales-invoice-full`, etc.
- **Xero**: `POST /create-xero-purchase-invoice`, `/create-xero-sales-invoice`, `/submit-xero-invoice`, `/create-payment-from-xero`, and related bank transaction routes.
- **CE**: `POST /create-ce-purchase-invoice`, `/create-ce-sales-invoice`; `PUT /invoice/:invoiceId/submitted` → `updateSubmittedInvoice` (amend submitted invoices from CE).
- **Bank context**: `GET /get-bank-transactions-by-invoice`, `/get-payment-entry-by-invoice-id` (supporting payment and bank linkage around invoices).

### `src/erpnext/erpnext.service.ts`

- **`getInvoiceByExtractionId` / `getInvoices`**: ERPNext resource API filtered by `extraction_id`.
- **`createInvoices`**: `frappe.desk.form.save.savedocs`.
- **`downloadAndUploadAttachment`**: moves attachments from Sleek receipts/Dext context into SleekBooks doc attachments (used from Dext and CE invoice create paths).
- **`getInvoiceDetailsWithPaymentEntryAndBankTransaction`**: `api/method/sleek.api.get_invoice_details` with `doctype`, `invoice_id`.
- **`getBulkInvoiceDetailsWithPaymentEntryAndBankTransaction`**: `api/method/sleek.api.get_bulk_invoice_details` with `doctype`, `invoice_ids`.
- **`createPurchaseInvoiceFromXero` / `createSalesInvoiceFromXero` / `submitInvoiceFromXero` / `createPaymentFromXero`**: Xero-shaped payloads into ERPNext purchase/sales invoices and payments.
- **`createPurchaseInvoiceFromCE` / `createSalesInvoiceFromCE`**: CE `DocumentDetails` → ERPNext forms; attachment upload errors logged; optional `DataStreamerService` publish patterns (see file for `CESleekBooksInvoiceDoneEvent` / `Failed`).
- **`updateSubmittedInvoice`**: `moveInvoiceToDraft` via `sleek.override_function.general_ledger.update_entry`, reload full PI/SI/JE, then `updateInvoiceFromCE`; rollback attempts re-submit of prior doc on failure.

### `src/kafka/listeners/invoice.listener.ts`

- **`@SubscribeEvent(CESleekBooksInvoiceCreatedEvent.name)`** → `onCESleekBooksInvoiceCreated` dispatches to `createPurchaseInvoiceFromCE` or `createSalesInvoiceFromCE` by `document_type` (purchase invoice, debit note, sales invoice, credit note, etc.).

### `src/erpnext/dto/get-invoice.dto.ts`

- **`GetInvoiceParamsDto`**, **`GetInvoiceQueryDto`**, **`GetInvoicesQueryDto`**, **`GetBulkInvoiceDetailsWithPaymentEntryAndBankTransactionDto`**: validation for extraction id, `docType` / `invoiceType` enums.

### `src/erpnext/interface/erpnext.interface.ts`

- **`PurchaseInvoiceFormData`**, **`SalesInvoiceFormData`**, **`extraction_id`**, payment and bank-related interfaces used when building or interpreting ERPNext documents.
