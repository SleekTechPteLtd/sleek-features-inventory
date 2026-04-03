# Sync purchase-related SleekBooks documents to ERPNext

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync purchase-related SleekBooks documents to ERPNext |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | When Customer Edge publishes purchase-side documents, payables and related expense records in ERPNext (SleekBooks) stay aligned with coding-engine data so finance can trust supplier bills, returns, payroll-linked costs, and contract spend in one ledger. |
| **Entry Point / Surface** | Backend integration: Kafka-style domain event `CESleekBooksInvoiceCreatedEvent` handled by `InvoiceListener` (`@Controller('invoice-listener')`); not an end-user screen. Upstream: Customer Edge / Coding Engine after document publish. |
| **Short Description** | On `CESleekBooksInvoiceCreatedEvent`, if `document_type` is purchase invoice, debit note, payslip/payroll, or contracts/agreement, the listener sets `is_return` for debit notes and calls `ErpnextService.createPurchaseInvoiceFromCE`. That resolves company (UEN), supplier, category/expense account, FX, builds purchase invoice form data via `createCEPurchaseInvoiceFormData`, submits through Frappe `savedocs` with action Submit, then applies tags/attachments and publishes `CESleekBooksInvoiceDoneEvent` or `CESleekBooksInvoiceFailedEvent` for downstream status. Sales invoices and credit notes route to `createSalesInvoiceFromCE` instead. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream** — Customer Edge / Coding Engine publishes `CESleekBooksInvoiceCreatedEvent` with `DocumentDetails` (`document_type` from `DocumentType` enum). **External** — ERPNext/Frappe REST (`frappe.desk.form.save.savedocs`, company/supplier/item helpers). **Downstream** — `DataStreamerService` emits `CESleekBooksInvoiceDoneEvent` / `CESleekBooksInvoiceFailedEvent` (handled elsewhere, e.g. coding engine publish-entry updates). **Related** — `sync-invoices-from-extraction-xero-and-ce.md` for broader CE/Xero invoice API surface; sales path in same listener for `sales_invoice` / `credit_note_or_refund`. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | None in this layer: `ErpnextService` persists via ERPNext HTTP APIs; no Mongoose collections in the purchase-from-CE path cited. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/kafka/listeners/invoice.listener.ts`

- **`@SubscribeEvent(CESleekBooksInvoiceCreatedEvent.name)`** → `onCESleekBooksInvoiceCreated`.
- **Purchase path** when `document_type` ∈ `payslip_or_payroll`, `contracts_and_agreement`, `purchase_invoice`, `debit_note`: sets `documentDetails.is_return` to `document_type === debit_note`, then **`erpnextService.createPurchaseInvoiceFromCE(documentDetails)`**.
- **Sales path** for `sales_invoice` or `credit_note_or_refund`: sets `is_return` for credit notes, calls **`createSalesInvoiceFromCE`**.
- Logs and skips other `document_type` values (e.g. `direct_transaction`).

### `src/kafka/events/ce-sleekbooks-invoice-created.event.ts`

- **`CESleekBooksInvoiceCreatedEvent`** extends `DomainEvent<DocumentDetails>`.

### `src/kafka/enum/document.enum.ts`

- **`DocumentType`**: `purchase_invoice`, `sales_invoice`, `direct_transaction`, `credit_note_or_refund`, `debit_note`, `contracts_and_agreement`, `payslip_or_payroll`.

### `src/kafka/interface/invoice.interface.ts`

- **`DocumentDetails`**: `uen`, `company_name`, `document_id`, `invoice_number`, dates, `document_type`, supplier/customer, category (`CoaData`), amounts, `line_items`, `publish_id`, optional `file_uri` / `file_uris`, `bank_account`, optional **`is_return`** (set by listener for debit/credit note semantics).

### `src/erpnext/erpnext.service.ts`

- **`createPurchaseInvoiceFromCE`**: `getCompaniesByFilter` (UEN), `checkDueDate`, `getSupplier`, `getInvoiceConversionRate`, derives base/net totals, **`createCEPurchaseInvoiceFormData`** → HTTP POST `api/method/frappe.desk.form.save.savedocs` with `action: 'Submit'`, then **`applyTagsAndAttachmentsForCEInvoice`**, **`dataStreamerService.publish(CESleekBooksInvoiceDoneEvent)`** on success or **`CESleekBooksInvoiceFailedEvent`** on error.
- **`createCEPurchaseInvoiceFormData`**: builds Purchase Invoice form (supplier, bill fields, `extraction_id` from `document_id`, line items via `formCEPurchaseLineItems`); when **`is_return`**, sets `formData.is_return = 1` and negates `total_qty`.
