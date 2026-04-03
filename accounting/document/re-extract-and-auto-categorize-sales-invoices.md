# Re-extract documents and auto-categorize sales invoices

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Re-extract documents and auto-categorize sales invoices |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (bulk re-extract); System / integrations (sales auto-categorization via API key) |
| **Business Outcome** | Receipt and invoice data stay aligned with the ledger when extraction must be rerun, and sales invoices can receive the correct default sales account without manual coding. |
| **Entry Point / Surface** | **acct-coding-engine** REST API: `POST /document/bulk-re-extract` (authenticated user); `POST /document/sales-invoices/auto-categorize` (API key). Consumer UIs are not defined in these files—likely Sleek bookkeeping / receipts flows that call the coding engine. |
| **Short Description** | Operators trigger a **bulk re-extraction** job (up to 50 document IDs per request, guarded against concurrent document jobs): each document is reset for extraction, events and streaming publish a **BookkeepingQueries** message to re-run ML extraction, and an audit log is written. Separately, **integrations** call an API-key endpoint to set the document category to the company chart-of-accounts entry whose name matches **`200 - Sales`** (system-populated), with events and auditor logging on success. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Chart of accounts** via `CoaService.getCompanyCoa` (Xero or SleekBooks by company ledger, Redis cache); **Kafka/streaming** (`BookkeepingQueriesEvent`) for re-extraction pipeline; **domain events** (`DocumentEventType.UPDATED`); **Sleek Auditor** for activity logs; **job processing** service to serialize document jobs and estimate completion. Downstream extraction/ML consumers are outside this controller/service pair. |
| **Service / Repository** | `acct-coding-engine` (Bitbucket-style: local path `acct-coding-engine`) |
| **DB - Collections** | MongoDB: **`documentdetailevents`** (documents read/updated); **`companies`** (read in CoA resolution for auto-categorization). Redis: COA cache keys `coa:{companyId}:{ledgerType}` (not a Mongo collection). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact product navigation labels for “bulk re-extract” in the Sleek app; which integrations call `sales-invoices/auto-categorize` in each environment. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/document/document.controller.ts`

- `POST document/bulk-re-extract` — `@UseGuards(AuthGuard, DocumentReExtractionGuard)`; body `documentIds: string[]`; `@ApiOperation` summary “Re-extract documents”; delegates to `DocumentService.handleReExtraction`.
- `POST document/sales-invoices/auto-categorize` — `@UseGuards(ApiKeyGuard)`; body `documentId`; `@ApiOperation` “Auto-categorize sales invoice with 200-Sales category”; delegates to `DocumentService.handleSalesInvoiceAutoCategorization`.

### `src/document/document.service.ts`

- `handleReExtraction` — creates a document job via `JobProcessingService.createDocumentJob`, returns `isProcessing`, `jobId`, `estimatedCompletionTime`; starts `processDocumentReExtraction` in the background.
- `processDocumentReExtraction` — loops document IDs, calls `reExtractSingleDocument`, `updateJobProgress`, throttles with `ProcessingTime.DOCUMENT`, `completeJob` / `addError` on failure.
- `reExtractSingleDocument` — `documentModel.findOneAndUpdate` sets `status: DocumentStatus.EXTRACTING`, clears duplicate flags; `eventUtils.publishEvent(DocumentEventType.UPDATED, …)`; `dataStreamerService.publish(BookkeepingQueriesEvent.EVENT_NAME, BookkeepingQueriesEvent)` with `FeedbackType.DOCUMENT_EVENT` and `s3_uri` / company / ledger; `sleekAuditorService.insertLogsToSleekAuditor` (“Document Re-extraction Initiated”).
- `handleSalesInvoiceAutoCategorization` — `documentModel.findById`; `coaService.getCompanyCoa(company)`; finds category where name matches `SALES_CATEGORY_NAME` (`200 - Sales` from `src/coa/interface/coa.interface.ts`); `documentModel.findByIdAndUpdate` sets `category` with `is_populated_by: CoaPopulatedBy.SYSTEM`; publishes `DocumentEventType.UPDATED`; auditor log “Sales Invoice Auto-categorization Success”.

### `src/document/middleware/document-re-extraction.middleware.ts`

- `DocumentReExtractionGuard` — requires 1–50 `documentIds`; `ConflictException` if another `document` job is already processing (with time remaining from `JobProcessingService`).

### `src/document/models/document.schema.ts`

- `@Schema({ collection: 'documentdetailevents', timestamps: true })` — primary document store for these flows.

### Related services (not in the listed files but directly invoked)

- `CoaService.getCompanyCoa` — loads company from **coding-engine** DB, fetches accounts from **Xero** or **SleekBooks**, caches in **Redis**.
