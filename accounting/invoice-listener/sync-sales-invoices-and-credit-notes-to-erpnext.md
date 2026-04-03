# Sync sales invoices and credit notes from SleekBooks to ERPNext

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync sales invoices and credit notes from SleekBooks to ERPNext |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Receivables and revenue in ERPNext stay aligned with Customer Edge–published sales documents in SleekBooks, including credit notes, so finance sees one consistent sales ledger. |
| **Entry Point / Surface** | Backend: Kafka event `CESleekBooksInvoiceCreatedEvent` handled by `InvoiceListener` (`@Controller('invoice-listener')`). No end-user UI; triggered when CE publishes an invoice-created payload. |
| **Short Description** | Subscribes to CE invoice-created events; when `document_type` is sales invoice or credit note, sets `is_return` for credit notes and calls `ErpnextService.createSalesInvoiceFromCE` to build and submit a Sales Invoice in ERPNext (including return/credit behaviour), attach files when present, and publish success or failure back via `CESleekBooksInvoiceDoneEvent` / `CESleekBooksInvoiceFailedEvent`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream** — Customer Edge / SleekBooks publishes `CESleekBooksInvoiceCreatedEvent` with `DocumentDetails` (`document_type` from `DocumentType` enum). **Same listener** also routes purchase-side types to `createPurchaseInvoiceFromCE` (out of scope for this feature row). **External** — ERPNext/Frappe REST (`frappe.desk.form.save.savedocs`), company and customer resolution by UEN/name, optional FX via `getExchangeRate`. **Downstream** — `DataStreamerService.publish` for done/failed events; optional tagging for direct transactions. **Related** — broader CE/Xero invoice sync in `accounting/erpnext/sync-invoices-from-extraction-xero-and-ce.md`. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | None in this service layer for this flow: documents are persisted via ERPNext HTTP APIs; no Mongoose models are used in `createSalesInvoiceFromCE`. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/kafka/listeners/invoice.listener.ts`

- **`@SubscribeEvent(CESleekBooksInvoiceCreatedEvent.name)`** → `onCESleekBooksInvoiceCreated` reads `message.data.document_type`.
- **Sales path**: `DocumentType.sales_invoice` or `DocumentType.credit_note_or_refund` → sets `documentDetails.is_return` when type is `credit_note_or_refund`, then **`erpnextService.createSalesInvoiceFromCE(documentDetails)`**.
- Other document types in the same handler go to purchase creation or are logged as invalid.

### `src/kafka/events/ce-sleekbooks-invoice-created.event.ts`

- **`CESleekBooksInvoiceCreatedEvent`** extends `DomainEvent<DocumentDetails>` — payload shape for CE invoice-created messages.

### `src/kafka/enum/document.enum.ts`

- **`DocumentType.sales_invoice`**, **`DocumentType.credit_note_or_refund`** — values used to branch the sales vs purchase paths in the listener.

### `src/kafka/interface/invoice.interface.ts`

- **`DocumentDetails`**: `uen`, `company_name`, `document_id`, `invoice_number`, dates, `document_type`, `customer_name`, `category` (COA), amounts, `line_items`, `publish_id`, optional `file_uri` / `file_uris`, **`is_return`** for credit/debit notes.

### `src/erpnext/erpnext.service.ts`

- **`createSalesInvoiceFromCE(documentDetails)`** (~5157–5297): loads company by UEN (`getCompaniesByFilter`), validates due date (`checkDueDate`), resolves customer (`getCustomer`), resolves income account from `category`, optional conversion rate when company currency differs from document currency, sets `base_total_amount` / `net_amount` / `base_grand_total`, builds payload via **`createCESalesInvoiceFormData`**.
- **ERPNext write**: `POST` `api/method/frappe.desk.form.save.savedocs` with `action: 'Submit'`.
- **Credit note**: `createCESalesInvoiceFormData` sets `formData.is_return = 1` and negates `total_qty` when `is_return` is true (from listener for `credit_note_or_refund`).
- **Attachments**: optional `processFileURIs` after create; attachment errors are logged, not thrown as overall failure.
- **Outcomes**: on success, **`dataStreamerService.publish(CESleekBooksInvoiceDoneEvent.name, …)`** with `document_id`, `publish_id`, `invoice_id` (ERPNext name), `link` to Sales Invoice; on failure, **`CESleekBooksInvoiceFailedEvent`** with `errors[]`.
