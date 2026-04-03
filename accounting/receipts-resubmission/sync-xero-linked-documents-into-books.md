# Sync Xero-linked documents into books

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync Xero-linked documents into books |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Document events that are already tied to a Xero invoice id can be reconciled against BigQuery-backed Xero invoice data so Sleek shows in-books status with correct amounts, tax, currency rate, and invoice references aligned to what was posted. |
| **Entry Point / Surface** | Sleek Receipts HTTP API: `POST /receipts-resubmission/sync/xero` (Bearer token `SLEEK_RECEIPTS_TOKEN` via `validateDocumentEventAuth` in `src/routes/receipts-resubmission.js`). Intended for internal or operations tooling rather than a standard Sleek App screen. |
| **Short Description** | Loads `DocumentDetailEvent` rows for a company and date range that have `hubdoc_data.xero_actions_remote_object_id` and caller-selected statuses; for each invoice id, reads one row from BigQuery `xero_invoices`, then updates the document via `updateDocumentEventDetailsByDocumentId` to `in_books` with Xero fields (type, dates, `InvoiceNumber`, currency, `Total`, `TotalTax`, `CurrencyRate`, etc.). Returns counts and per-document success/failure lists. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Requires Hubdoc (or upstream) to have stored `xero_actions_remote_object_id` on the document (`updateDocumentEventHubdocData`). Upstream data: Google BigQuery project/dataset from `BQPROJECTID` + `BQDATASET` (`authBQ`). Related but different: batch script `get-xero-client-invoices` syncs from the **live** Xero API and line categories; this endpoint uses **BigQuery** `xero_invoices` only (no line-level categories; code notes TODO for category). Same module also exposes `POST /receipts-resubmission/process/bulk` for bulk receipt resubmission (`processBulkSRS`), which is a separate flow. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `documentdetailevents` (read `DocumentDetailEvent`, update via `updateDocumentEventDetailsByDocumentId`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | How often BigQuery `xero_invoices` is refreshed vs live Xero; whether operations rely on this vs the live-API script for the same reconciliation goal; market-specific scope not stated in code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Routes (`src/routes/receipts-resubmission.js`)

- **`POST /receipts-resubmission/sync/xero`** → `syncDocumentsFromXero`; guarded by `validateDocumentEventAuth()` (header `Authorization` must equal `process.env.SLEEK_RECEIPTS_TOKEN`).

### Controller (`src/controllers/receipts-resubmission.controller.js`)

- **`syncDocumentsFromXero`:** passes `req.body` to `receiptsResubmissionService.syncDocumentsFromXero`; success code `SYNC_DOCUMENTS_FROM_XERO`.

### Receipts resubmission service (`src/services/receipts-resubmission.service.js`)

- **`syncDocumentsFromXero(options)`:** destructures `company`, `start_date`, `end_date`, `statuses`, `offset`, `limit`; `authBQ()` for `BQInstance` and `DB_NAME`.
- **`DocumentDetailEvent.find`:** `company`, `hubdoc_data.xero_actions_remote_object_id` exists and non-empty, `submission_date` within range, `status` in `statuses`, not deleted/archived; `skip`/`limit`.
- Per document: `invoiceId` from `hubdoc_data.xero_actions_remote_object_id`; **`getXeroInvoiceByInvoiceId(BQInstance, DB_NAME, invoiceId)`**; if rows returned, maps `Type`, `DateString`, `InvoiceNumber`, `DueDateString`, `CurrencyCode`, `CurrencyRate`, `Total`, `TotalTax` into **`updateDocumentEventDetailsByDocumentId`** with `status: DOCUMENT_EVENT_STATUSES.IN_BOOKS` and the monetary/reference fields; accumulates `successfulEntries` / `failedEntries`.
- Returns `{ allCount, updatedCount, options, successfulEntries, failedEntries }`.

### Document event service (`src/services/document-event-service.js`)

- **`updateDocumentEventDetailsByDocumentId`:** validates ObjectId, **`computeDocumentEventDetails`** (for `IN_BOOKS`, derives `converted_total_amount` / `converted_total_tax_amount` from totals and `currency_rate` when present), **`validateDuplicateDocuments`**, `DocumentDetailEvent.updateOne` `$set` including `is_duplicated`.

### BigQuery (`src/bigquery/bigquery-utilities.js`)

- **`authBQ`:** `@google-cloud/bigquery` with `BQPROJECTID`, `GOOGLE_APPLICATION_CREDENTIALS` / key file, `BQDATASET` → qualified **`DB_NAME`**.
- **`getXeroInvoiceByInvoiceId(bigquery, databaseName, invoiceId)`:** `SELECT * FROM ${databaseName}.xero_invoices WHERE InvoiceID = "${invoiceId}" LIMIT 1`, location `asia-southeast1`.

### Same file, separate capability (context only)

- **`processBulkSRS` / `processBulkSRS` controller:** bulk receipt reprocessing from BigQuery `getUnprocessedReceipts` or Mongo aggregate; calls **`processSRS`** from `webhook-service` — not the Xero sync path above.
