# Apply ERPNext invoice data to documents

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Apply ERPNext invoice data to documents |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Document records in DSS stay aligned with invoice data produced after ERPNext-side processing, so bookkeepers see correct amounts, references, supplier, and categorisation without manual re-keying. |
| **Entry Point / Surface** | Server-to-server: `POST /webhook/invoice/submit` on Sleek Receipts (ERPNext webhook). Authenticated with `Authorization` header matching `SLEEK_RECEIPTS_TOKEN` (`validateDocumentEventAuth`). Not an end-user screen. |
| **Short Description** | ERPNext posts an invoice payload (including `extraction_id`). The service resolves the Dext event by external id and the linked document event, then updates document fields (status, doc type, dates, references, amounts, supplier, description, category line items) and duplicate detection so the document matches external extraction outcomes. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** ERPNext pushes webhooks; Dext events must exist with `external_id` matching `extraction_id`, and a `DocumentDetailEvent` must reference that Dext event via `dext_event`. **Related:** ML extraction webhook (`POST /webhook/ml-extraction`) and Dext/Hubdoc flows feed other document updates; company settings may store `erpnext_ids` for integration context. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `documentdetailevents` (reads/updates via `DocumentDetailEvent`); `dextevents` (read via `DextEvent.findOne({ external_id })`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | On failure, `receiveERPNextInvoiceData` logs the error but does not send an HTTP error response—confirm whether callers rely on this and if responses should be added. Markets/variants for ERPNext rollout not visible in these files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Route:** `src/routes/webhook.js` — `POST /invoice/submit` → `WebhookController.receiveERPNextInvoiceData`, guarded by `validateDocumentEventAuth()`; app mounts router at `/webhook` (`index.js`), so full path **`POST /webhook/invoice/submit`**.
- **Auth:** `src/middleware/document-event-middleware.js` — `Authorization` header must equal `process.env.SLEEK_RECEIPTS_TOKEN`.
- **Controller:** `src/controllers/webhook-controller.js` — `receiveERPNextInvoiceData` logs body, calls `documentEventService.updateDocumentEventByExtractionId(body)`, success via `successResponseHandler` with `SUCCESS_CODES.WEBHOOK_CODES.RECEIVE_ERPNEXT_INVOICE_DATA` (`src/constants/success-message.js` message: successfully received ERPNext invoice data).
- **Service:** `src/services/document-event-service.js` — `updateDocumentEventByExtractionId(invoice)` destructures `extraction_id, doctype, supplier, items, due_date, currency, total, base_total, bill_no, bill_date`; finds `DextEvent` by `external_id: extraction_id`, then `DocumentDetailEvent` by `dext_event: dextEvent._id`; builds status from receipt type (`IN_BOOKS` vs `EXP_CLAIM_REPORT` for expense-claim types); `mapLineItems` maps `items` to `category` entries; runs `validateDuplicateDocuments`; `DocumentDetailEvent.updateOne` with merged fields and `is_duplicated`.
- **Schemas:** `src/schemas/document-detail-event.js`, `src/schemas/dext-event.js` — fields updated match document event and Dext linkage model.
