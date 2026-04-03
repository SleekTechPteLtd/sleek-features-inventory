# Submit receipts and expense documents

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Submit receipts and expense documents |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User, Operations User (submitter); integrations and email-in flows act as System |
| **Business Outcome** | Receipts and attachments become structured document events, enter ML extraction, and can be forwarded to Dext (Receipt Bank) or Hubdoc for downstream bookkeeping. |
| **Entry Point / Surface** | Sleek App and connected clients that call sleek-receipts APIs; `POST /document-events/submit-receipt` and `POST /document-events/submit-receipt-v2` (multipart, `validateDocumentEventAuth`). |
| **Short Description** | Users submit files with company, receipt type, and ledger context. The service validates the company receipt system, normalises files (including optional PDF conversion for images/office/zip), stores each attachment on S3, creates document records in extracting status, triggers ML extraction, publishes Kafka events, and emails documents to the configured Dext or Hubdoc address when the legacy “forward” path applies. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | ML extraction (`getExtractionDataApi` / ml-node-server); S3 upload (`FileUploader`); optional auto-categorisation for sales invoices (`coding-engine-service`); Kafka `DOCUMENT_CREATED`; Dext/Hubdoc forwarding (`EmailForwarder.sendToReceiptBankOrHubdoc` / `sendToReceiptBankOrHubdocV2`); office/HEIC conversion (`sleek-conversion-services`, `pdf-utils`); company ledger checks (`company-setting-utils`); Hubdoc callback data via `PUT /document-events/hubdoc`. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `documentdetailevents` (mongoose model `DocumentDetailEvent`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether market-specific behaviour is configured outside this repo (tenant `shared-data.json` only partially visible here); exact product labels for “Sleek App” navigation. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Routes and auth (`src/routes/document-event.js`)

- `POST /document-events/submit-receipt` — `multipartHandler`, `validateDocumentEventAuth`, `submitReceiptEvent`.
- `POST /document-events/submit-receipt-v2` — same guards, `submitReceiptEventV2`.
- Auth: `Authorization` header must equal `process.env.SLEEK_RECEIPTS_TOKEN` (`document-event-middleware.js`).

### Controller (`src/controllers/document-event-controller.js`)

- **`submitReceiptEvent`**: Resolves user/company via `UserDetails.getUserDetails` or `getUserDetailsV2` when `EMAIL_FORWARDING_V2_ENABLED` and `emailInAddress` are set. Validates company `receipt_system_status` is `ACTIVE`, non-empty files, and receipt type in expense/revenue accepted lists. Builds `images` either with `getPDFContent` (when `document_submission_data_flow_v2` tenant feature is on) or raw base64 per file. Calls `documentEventService.createDocumentEvent` then `EmailForwarder.sendToReceiptBankOrHubdoc` or `sendToReceiptBankOrHubdocV2`. Uses `getAddressDestination(ledger, receiptType)` for V2 forwarding destination.
- **`submitReceiptEventV2`**: Uses `files['files[]']`, `getPDFContentV2`, `createDocumentEvent` with 201 response and `attachmentIds`.

### Service (`src/services/document-event-service.js`)

- **`createDocumentEvent(files, documentDetails, source)`**: For each image in `documentDetails.images`, validates file, `DocumentDetailEvent.create` with status `EXTRACTING`, `createDocumentLogger`, uploads to S3, sets `file_url` / `file_uri`, calls `getExtractionDataApi` with `DOCUMENT_TYPE.DOCUMENT_EVENT`, `cloneDocumentEventToMLFeedback`, saves, `KafkaService.publishEvent(DocumentEventType.DOCUMENT_CREATED, ...)`. Sales invoice path triggers `CODING_ENGINE_API.autoCategorizeSalesInvoice`.

### Email forwarding (`src/messages/email-forwarder.js`)

- **`sendToReceiptBankOrHubdoc` / `sendToReceiptBankOrHubdocV2`**: If company receipt system is already active, skips forward (`return true`). Otherwise sends via `EmailSender.sendEmail` to Dext (`receipt_bank_address`) or Hubdoc (`company.hubdoc_address`) depending on receipt type / `addressDestination`; may attach S3-named files via `renameImagesFilename`.

### PDF and file handling (`src/utils/pdf-utils.js`)

- **`getPDFContent`**: Unzips when enabled; converts images to PDF for Dext or SleekBooks ERP ledger; converts Office types to PDF when enabled and type is Dext/Hubdoc; uses `conversionService.getConvertedFile` for office conversion.
- **`getPDFContentV2`**: HEIC to JPEG, optional office-to-PDF, zip expansion.
