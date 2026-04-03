# Bulk reprocess receipt submissions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Bulk reprocess receipt submissions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operations can replay receipt submission processing for batches of stuck or failed flows so documents reach processing again without manual one-off fixes. |
| **Entry Point / Surface** | Sleek Receipts service HTTP API: `POST /receipts-resubmission/process/bulk` (shared auth with `POST /receipts-resubmission/sync/xero`). Caller must send `Authorization` header matching `SLEEK_RECEIPTS_TOKEN`; no app navigation path is defined in this repo. |
| **Short Description** | Accepts filters (company, date range, sources, receipt types, statuses, pagination). Either loads candidate receipts from BigQuery view `sq_tb_receipts_to_retrigger` or, when `is_document_retrigger` is true, from MongoDB `DocumentDetailEvent` documents. Each row is normalized and passed to `processSRS`, which resolves the user, loads the file from S3 or an external URL, and re-sends the receipt pipeline email with `is_retrigger: true` while setting the document event to `processing`. Returns counts of successes and failures per receipt. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **BigQuery** (`BQPROJECTID_V2`, `BIGQUERY_CREDENTIALS`, view `gds_views.sq_tb_receipts_to_retrigger`); legacy BQ auth for Xero invoice reads (`BQPROJECTID`, `BQDATASET`, `xero_invoices`). **Internal:** `processSRS` (`webhook-service`) → `UserDetails`, S3 (`RECEIPTS_S3_BUCKET`), `EmailForwarder.sendToReceiptBankOrHubdoc`, `documentEventService.updateDocumentEventStatusByDocumentId`. **Related endpoint (same module):** `POST /receipts-resubmission/sync/xero` refreshes document fields from Xero via BigQuery for documents with `hubdoc_data.xero_actions_remote_object_id` — not the same as bulk SRS replay but adjacent ops tooling. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | Mongoose defaults: `documentdetailevents` (`DocumentDetailEvent` — aggregate/find/update for retrigger and sync paths), `receiptresubmissions` (`ReceiptResubmission` — audit log per replay attempt). BigQuery datasets/views as above (not Mongo collections). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether `limit` / `offset` omitted or zero is intentional (Mongo `$limit: 0` returns no documents). Product surface that calls these routes (internal script, gateway, or admin UI) is not in this repo. Market-specific behavior not evidenced in code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/routes/receipts-resubmission.js`

- `POST /receipts-resubmission/process/bulk` → `receiptsResubmissionController.processBulkSRS`, guarded by `validateDocumentEventAuth()`.
- `POST /receipts-resubmission/sync/xero` → `syncDocumentsFromXero` (same middleware).

### `src/middleware/document-event-middleware.js`

- `validateDocumentEventAuth`: requires `req.headers.authorization === process.env.SLEEK_RECEIPTS_TOKEN`.

### `src/controllers/receipts-resubmission.controller.js`

- `processBulkSRS`: passes `req.body` to `receiptsResubmissionService.processBulkSRS`; success code `SUCCESS_CODES.RECEIPTS_RESUBMISSION_CODES.PROCESS_BULK_RECEIPTS`.

### `src/services/receipts-resubmission.service.js`

- **`processBulkSRS`**: If `is_document_retrigger`, aggregates `DocumentDetailEvent` by `company`, `paid_by` / `submission_date` / `status`, `is_deleted` / `is_archived`, with `$facet` for count + paginated docs. Else `getUnprocessedReceipts(BQInstance, projectId, options)` from BigQuery V2.
- **`formatReceiptsData`**: Maps BQ or doc rows into payloads for `processSRS` (`file_url`, `user_email`, `receipt_user`, `company_name`, `emaillogs_id` as `log_id`, `company_id`, `phone_number`, `target`, `source`, fixed `submitter_email` `accounting@sleek.com`).
- **`processBulkSRS`**: `Promise.all` of `processSRS(receipt)`; aggregates `failed_receipts` where result `status === 'error'`.
- **`syncDocumentsFromXero`**: `DocumentDetailEvent.find` with `hubdoc_data.xero_actions_remote_object_id`, date/status filters; `getXeroInvoiceByInvoiceId` → `updateDocumentEventDetailsByDocumentId` to `IN_BOOKS` and Xero-derived fields.

### `src/bigquery/bigquery-utilities.js`

- **`getUnprocessedReceipts`**: Queries `${projectId}.gds_views.sq_tb_receipts_to_retrigger` with filters on `present_in_dss`, `present_in_dext_hubdoc`, `has_xero_match_in_ml_matching`, `sender_status`, date range, optional `sources`, `receipt_types`, `company`; maps source/receipt_type labels via `CASE`.

### `src/services/webhook-service.js`

- **`processSRS`**: Creates `ReceiptResubmission` record; resolves user via `UserDetails` (by `receipt_user`, or WhatsApp + company, or email + company); builds PDF/images via S3 or external URL (`axios`); `getDocumentEventDetails` → existing `DocumentDetailEvent` by id or `createDocumentEvent`; on success sends `EmailForwarder.sendToReceiptBankOrHubdoc` with `is_retrigger: true`, `old_email_log_id`; updates document status to `DOCUMENT_EVENT_STATUSES.PROCESSING`; persists `ReceiptResubmission` with `ZOHO_SRS_STATUSES` success/error.

### `src/schemas/receipt-resubmission.js`

- Model `ReceiptResubmission`: `email_log`, `document_event`, `file_url`, `source`, `receipt_type`, `status`, `document_error_logs`, etc.

### `src/schemas/document-detail-event.js`

- Model `DocumentDetailEvent`: company, receipt_user, source, status, `paid_by`, `hubdoc_data`, etc.
