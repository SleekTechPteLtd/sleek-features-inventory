# Review document intake and sources

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Review document intake and sources |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, Bookkeeper, Finance User (via Sleek client apps and tools that call sleek-receipts; API is service-authenticated) |
| **Business Outcome** | Teams can list receipt document events in scope (company or global operational views), see per-user read state where applicable, and open human-readable file content for a document or external extraction id so intake can be reviewed and processed with full context. |
| **Entry Point / Surface** | Sleek App / bookkeeping document list and detail flows (aligned with service comments for list/detail views); sleek-receipts HTTP API: `GET /document-events`, `GET /document-events/companies/:companyId`, `GET /document-events/:documentId`, `GET /document-events/readable-src/:documentId`, `GET /document-events/readable-src/extraction/:extractionId` (all behind `validateDocumentEventAuth` / `Authorization: SLEEK_RECEIPTS_TOKEN`) |
| **Short Description** | Lists document events with pagination, search, filters (status, source, paid-by, archive/delete/duplicate flags, date range, ledger, user-scoped read status), scoped by company or across all events. Returns a single document by id. Resolves readable preview content from S3 for a document id, or by Hubdoc/Dext extraction id and type query. Supports marking documents as read for a user. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Document creation and extraction (`createDocumentEvent`, ML `getExtractionDataApi`); `document-event-utils.getReadableSrc` / `getFileContent` and S3 `FileUploader`; company and receipt-user scoping; optional `DocumentReadStatus` join for unread indicators; Hubdoc/Dext pipelines for extraction-based readable source; related listing/ops usage referenced from sleek-robot for retrigger flows. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `documentdetailevents` (DocumentDetailEvent), `documentreadstatuses` (DocumentReadStatus — aggregation `$lookup` and `markDocumentAsRead`), `dextevents` (DextEvent when `readable-src/extraction` uses Dext type) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Routes and auth (`src/routes/document-event.js`, `src/middleware/document-event-middleware.js`)

- `GET /document-events` → `getAllDocumentEvents` — `validateDocumentEventAuth`: header `Authorization` must equal `process.env.SLEEK_RECEIPTS_TOKEN`.
- `GET /document-events/companies/:companyId` → `getAllDocumentEventsByCompanyId` — same guard.
- `GET /document-events/:documentId` → `getDocumentEventByDocumentId` — same guard.
- `GET /document-events/readable-src/:documentId` → `getDocumentEventReadableSrcByDocumentId` — same guard.
- `GET /document-events/readable-src/extraction/:extractionId` → `getDocumentEventReadableSrcByExtractionId` — query `type` for Hubdoc vs Dext (`EXTRACTION_TYPES`); same guard.
- `POST /document-events/mark-as-read` → `markDocumentAsRead` — same guard.

### Controller (`src/controllers/document-event-controller.js`)

- `getAllDocumentEvents`, `getAllDocumentEventsByCompanyId`, `getDocumentEventByDocumentId`, `getDocumentEventReadableSrcByDocumentId`, `getDocumentEventReadableSrcByExtractionId`, `markDocumentAsRead` delegate to `document-event-service`.

### Service — list, detail, readable source, read status (`src/services/document-event-service.js`)

- **`getAllDocumentEvents`**: Aggregation with optional search on `status`, comma-separated `statuses`, optional Hubdoc Xero link filter (`isHubdoc`), `$facet` metadata + paginated data (`skip`, `limit`, `sortOrder`, `fetchAll`).
- **`getAllDocumentEventsByCompanyId`**: Comment notes use on list/detail views. Matches `company` + `ledger`; filters by `receiptUserId`, date range, `filterByMonth`, search on id string / supplier / `total_amount`, `sources`, `statuses`, `paidBy`, archive/delete/request-delete/duplicate flags. `$lookup` from `documentreadstatuses` when `user` query present; `$project` strips `file_url`, `file_uri`, `file_uri_ml` from list payload; facets for monthly claim/document counts and amounts.
- **`getDocumentEventByDocumentId`**: `DocumentDetailEvent.findById` after ObjectId validation.
- **`getDocumentEventReadableSrcByDocumentId`**: Loads document; `documentEventUtils.getReadableSrc` with `DOCUMENT_SOURCES.DOCUMENT_EVENT`; returns `{ readable_src }` from encoded S3 buffer.
- **`getDocumentEventReadableSrcByExtractionId`**: Hubdoc path: `DocumentDetailEvent.findOne({ 'hubdoc_data.external_id': extractionId })`; Dext path: `DextEvent.findOne({ external_id: extractionId })`; then `getFileContent(fileURI)` returning base64 content, content type, filename.
- **`markDocumentAsRead`**: Upserts `DocumentReadStatus` for `(user, document)`.

### Utils (`src/utils/document-event-utils.js`)

- **`getReadableSrc`**: Resolves S3 `file_uri`, fetches object, sets `readableSrc` via `fileUtils.encodeDocument`.
- **`getFileContent`**: S3 fetch for extraction-based response used by readable-src-by-extraction.

### Schemas

- `src/schemas/document-detail-event.js` — model `DocumentDetailEvent`.
- `src/schemas/document-read-status.js` — model `DocumentReadStatus`.
- `src/schemas/dext-event.js` — `DextEvent` (referenced for extraction id readable path).
