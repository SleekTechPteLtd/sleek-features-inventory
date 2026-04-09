# Sync Hubdoc receipt events with Xero invoice data

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync Hubdoc receipt events with Xero invoice data |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Hubdoc-linked receipts that are still in processing get their Sleek document event updated from current Xero invoice facts returned via Sleek Back so amounts, dates, tax, currency, and references match Xero and status moves to in-books—keeping bookkeeping aligned with the ledger. |
| **Entry Point / Surface** | Backend batch script `src/scripts/get-xero-invoice.js` (MongoDB connect + `main()`); intended for scheduled or operator execution, not an end-user Sleek App screen. |
| **Short Description** | Loads up to ten Hubdoc-linked document events in `processing` with a non-null `hubdoc_data.xero_actions_remote_object_id`, groups invoice IDs by company, and calls Sleek Back `POST external-receipts/fetch-xero-invoice` to retrieve Xero invoice payloads. For each returned invoice, finds the matching `DocumentDetailEvent` by Xero invoice ID and updates it to `in_books` with document type, dates, invoice number, due date, currency, totals, tax, currency rate, and supplier—via `updateDocumentEventDetailsByDocumentId` (including duplicate checks and converted amounts when applicable). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Sleek Back** (`getXeroDataByInvoiceId` → `external-receipts/fetch-xero-invoice`) as the path to Xero invoice data; Hubdoc / upstream flows that populate `hubdoc_data` and `xero_actions_remote_object_id` (`updateDocumentEventHubdocData` elsewhere). Related but distinct: `get-xero-client-invoices.js` uses direct Xero API and BigQuery tenant/account resolution; this script delegates fetch to Sleek Back. Downstream: list/detail views reading `DocumentDetailEvent`. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `documentdetailevents` (read/update via Mongoose model `DocumentDetailEvent`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Production schedule, ownership, and alerting for this script are not defined in the repository; whether the Sleek Back endpoint applies region-specific Xero behaviour is not visible from this repo; script processes only the first page (`limit: 10`) of processing Hubdoc events—broader backfill behaviour is unspecified. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Batch script (`src/scripts/get-xero-invoice.js`)

- **`main`:** `documentEventService.getAllDocumentEvents({ skip: 0, limit: 10, search: '', statuses: DOCUMENT_EVENT_STATUSES.PROCESSING, isHubdoc: true })`; builds per-company lists of `hubdoc_data.xero_actions_remote_object_id`; merges duplicate company keys in a hash map; calls `SLEEK_BACK_API.getXeroDataByInvoiceId(mergedInvoices)`.
- **`updateDocumentEventByXeroData`:** reads `data.data` from the API response; for each Xero invoice uses `InvoiceID`, `Type`, `DateString`, `InvoiceNumber`, `DueDateString`, `CurrencyCode`, `CurrencyRate`, `Total`, `TotalTax`; `DocumentDetailEvent.findOne({ "hubdoc_data.xero_actions_remote_object_id": InvoiceID })`; `updateDocumentEventDetailsByDocumentId` with `status: IN_BOOKS`, `document_type`, `document_date`, `document_reference`, `due_date`, `currency`, `total_amount`, `total_tax_amount`, `converted_total_amount`, `converted_total_tax_amount`, `currency_rate`, `supplier` from existing `hubdoc_data`.
- **Boot:** `dotenv-flow`, `databaseServer.connect()`, logs counts and duration, `process.exit()`.

### Sleek Back client (`src/external-api/sleek-back.js`)

- **`getXeroDataByInvoiceId`:** `POST` to `external-receipts/fetch-xero-invoice` with body `{ invoices }` (company + invoice id groupings from the script), via `AXIOS_DEFAULTS.createDefaultAxiosObject`.

### Document updates (`src/services/document-event-service.js`)

- **`getAllDocumentEvents`:** aggregation on `DocumentDetailEvent` with optional `statuses`, `isHubdoc` filter requiring `hubdoc_data.xero_actions_remote_object_id` not null; `$facet` for metadata + paginated data.
- **`updateDocumentEventDetailsByDocumentId`:** validates ObjectId; `computeDocumentEventDetails` (e.g. `converted_total_amount` / `converted_total_tax_amount` when `IN_BOOKS` and `currency_rate` present); `validateDuplicateDocuments`; `DocumentDetailEvent.updateOne` with `$set` including `is_duplicated`.

### Schema (`src/schemas/document-detail-event.js`)

- **Model `DocumentDetailEvent`:** fields include `status`, `hubdoc_data`, monetary fields (`total_amount`, `converted_total_amount`, `total_tax_amount`, `converted_total_tax_amount`, `currency_rate`), `document_type`, `document_date`, `document_reference`, `due_date`, `currency`, `supplier`; Mongoose collection name lowercased plural `documentdetailevents`.
