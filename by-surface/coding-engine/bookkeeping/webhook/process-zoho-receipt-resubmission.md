# Process Zoho receipt resubmission

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Process Zoho receipt resubmission |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | When Zoho signals a receipt resubmission (from email or WhatsApp–driven flows), the platform records the attempt and either creates a new document in the DSS path or retriggers an existing document so downstream extraction and bookkeeping processing can continue. |
| **Entry Point / Surface** | **Inbound integration:** Zoho → Sleek Receipts `POST /webhook/zoho/srs` (Express app in repo root `index.js` mounts the webhook router at `/webhook`). Secured with `validateDocumentEventAuth()` (caller must send `Authorization` matching `SLEEK_RECEIPTS_TOKEN`). No in-app navigation; this is a server-to-server webhook. |
| **Short Description** | Accepts a Zoho payload (`submitter_email`, `file_url`, `company_name`, `user_email`, `target`, `source`, `emaillogs_id`, `company_id`, `phone_number`, `receipt_user`). Creates a `ReceiptResubmission` audit row, resolves the receipt user (explicit id, WhatsApp + company, or email + company), loads the file from Sleek S3 or an external URL, and either creates a new `DocumentDetailEvent` (when the parsed filename is not a Mongo id) or loads an existing event by id. On success it forwards to Receipt Bank / Hubdoc with `is_retrigger: true` and sets the linked document event status to `processing`. Errors are recorded on the resubmission record. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** Zoho (webhook caller). **Internal:** `UserDetails` (user resolution), S3 (`RECEIPTS_S3_BUCKET`) and optional external URL fetch (`axios`), `EmailForwarder.sendToReceiptBankOrHubdoc`, `documentEventService.createDocumentEvent` (new DSS-linked document + ML extraction kickoff) and `updateDocumentEventStatusByDocumentId` (retrigger path). **Related:** `POST /receipts-resubmission/process/bulk` reuses `processSRS` for operational bulk replay — same core logic, different entry. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | Mongoose defaults: `receiptresubmissions` (`ReceiptResubmission`), `documentdetailevents` (`DocumentDetailEvent` — create, find by id, status update). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Code TODOs note possible follow-ups (retrigger failed entries, dashboard visibility of errors, receipt type / expense-claim PDF handling). Market-specific behaviour is not evidenced in these files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/routes/webhook.js`

- `POST /zoho/srs` → `WebhookController.processManualSRS`, guarded by `validateDocumentEventAuth()`.

### `index.js` (repo root, mount)

- `app.use("/webhook", WebhookRouter)` → full path **`POST /webhook/zoho/srs`**.

### `src/middleware/document-event-middleware.js` (referenced by route)

- `validateDocumentEventAuth`: `req.headers.authorization === process.env.SLEEK_RECEIPTS_TOKEN`.

### `src/controllers/webhook-controller.js`

- **`processManualSRS`**: Logs Zoho body, calls `webhookService.processSRS(body)`, returns success via `successResponseHandler` / errors via `errorResponseHandler`.

### `src/services/webhook-service.js`

- **`processSRS`**: Documented scenarios — no existing DSS connection → create; existing connection → retrigger to processing. Creates `ReceiptResubmission` via `createReceiptResubmission`, resolves user (`UserDetails.getUserDetailsV2`, `getReceiptUserByWhatsappAndCompanyId`, or `getUserDetails`), builds attachments via `createImageAttachment` (S3 or external URL), **`getDocumentEventDetails`** → if parsed filename is not a valid ObjectId calls **`documentEventService.createDocumentEvent`** with `messagePayload` + `receiptUserDetails` and `source`; else **`DocumentDetailEvent.findById`** and optional `fileAttachments` from `file_url`. On eligible company + user: **`EmailForwarder.sendToReceiptBankOrHubdoc`** with `is_retrigger: true`, **`documentEventService.updateDocumentEventStatusByDocumentId`** with `DOCUMENT_EVENT_STATUSES.PROCESSING`. Sets `ZOHO_SRS_STATUSES` success/error and persists error logs when document missing, document errors, or user ineligible.

### `src/services/document-event-service.js`

- **`createDocumentEvent`**: Creates `DocumentDetailEvent` (status `extracting` → upload S3 → `getExtractionDataApi` for ML, etc.) — used when resubmission does not reference an existing document id.
- **`updateDocumentEventStatusByDocumentId`**: Updates `DocumentDetailEvent` status (used to move existing documents to `processing` on successful retrigger path).

### `src/schemas/receipt-resubmission.js` / `src/schemas/document-detail-event.js`

- Models backing `ReceiptResubmission` and `DocumentDetailEvent` persistence (see bulk resubmission inventory doc for field-level detail).
