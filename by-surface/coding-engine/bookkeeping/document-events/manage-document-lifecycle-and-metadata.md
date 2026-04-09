# Manage document lifecycle and metadata

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage document lifecycle and metadata |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Bookkeeper, Finance User (via clients calling sleek-receipts); System (sleek-robot / integrations for Hubdoc sync) |
| **Business Outcome** | Receipt and intake documents stay current: users and integrations can correct workflow status and extracted details, attach Hubdoc/Xero linkage data, record per-user read state, and archive or unarchive records so lists and downstream systems reflect reality. |
| **Entry Point / Surface** | Sleek App / internal tools using document list and detail views (service comments reference listView/detailView); sleek-receipts HTTP API under `/document-events` (shared service token). |
| **Short Description** | Updates document event status and editable fields (including currency conversion helpers and duplicate detection), accepts Hubdoc payload updates keyed by original filename, records “read” in a per-user collection, and bulk-archives, unarchives, soft-deletes, or requests deletion with optional Zendesk/email side effects. Publishes Kafka events on bulk lifecycle changes. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Hubdoc/Xero pipeline (external `hubdoc_data`); ML extraction (`getExtractionDataApi`) and Dext flows for details populated elsewhere; Coding Engine audit logs on some paths; Kafka consumers for `DOCUMENT_CREATED`, `BULK_DOCUMENT_ARCHIVED`, `BULK_DOCUMENT_UNARCHIVED`, `BULK_DOCUMENT_DELETED`, `DOCUMENT_UPDATED`; Zendesk/email for request-delete; company document lists that aggregate with `documentreadstatuses` lookup. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `documentdetailevents` (DocumentDetailEvent), `documentreadstatuses` (DocumentReadStatus; read tracking and `$lookup` on company lists) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `getAllDocumentEventsByCompanyId` uses `isDeleted === 'true'` with an `$match` on `is_archived: true` (same pattern as archive filter)—confirm whether “deleted” filtering is intentional or a copy-paste bug. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Routes and auth (`src/routes/document-event.js`, `src/middleware/document-event-middleware.js`)

- All routes use `validateDocumentEventAuth()`: header `Authorization` must equal `process.env.SLEEK_RECEIPTS_TOKEN`.
- Lifecycle/metadata endpoints:
  - `PUT /document-events/:documentId/status` → `updateDocumentEventStatusByDocumentId`
  - `PUT /document-events/:documentId/details` → `updateDocumentEventDetailsByDocumentId`
  - `PUT /document-events/hubdoc` → `updateDocumentEventHubdocData`
  - `POST /document-events/mark-as-read` → `markDocumentAsRead`
  - `PUT /document-events/actions/archive` → `archiveMultipleDocumentEventDetails`
  - `PUT /document-events/actions/unarchive` → `unarchiveMultipleDocumentEventDetails`
  - `PUT /document-events/actions/delete` → `deleteMultipleDocumentEventDetails`
  - `PUT /document-events/actions/request-delete` → `requestDeleteMultipleDocumentEventDetails`
- List/detail reads: `GET /document-events/companies/:companyId`, `GET /document-events/:documentId`, readable-src routes (supporting UI).

### Controller (`src/controllers/document-event-controller.js`)

- Passes `documentId` / body payloads to `document-event-service` for status, details, Hubdoc body, bulk ids, and `markDocumentAsRead(userId, documentId)`.

### Service (`src/services/document-event-service.js`)

- **`updateDocumentEventStatusByDocumentId`**: Validates `documentId` and status against `DOCUMENT_STATUSES`; `DocumentDetailEvent.updateOne` sets `status`.
- **`updateDocumentEventDetailsByDocumentId`**: `computeDocumentEventDetails` for converted amounts/rates by status; `validateDuplicateDocuments`; `updateOne` with merged fields and `is_duplicated`.
- **`updateDocumentEventHubdocData`**: Parses `original_filename` to document ObjectId; sets nested `hubdoc_data` (`external_id`, `xero_actions_remote_object_id`, `time_extracted`, `supplier`). Comments note Xero archived + invoice ref expectations from sleek-robot and ERPNext submission paths.
- **`markDocumentAsRead`**: `DocumentReadStatus` find-or-create for `(user, document)`.
- **`archiveMultipleDocumentEventDetails` / `unarchiveMultipleDocumentEventDetails`**: `updateMany` on `is_archived`; `KafkaService.publishEvent` with `BULK_DOCUMENT_ARCHIVED` / `BULK_DOCUMENT_UNARCHIVED`.
- **`deleteMultipleDocumentEventDetails`**: Audit log, `is_deleted` + clears archive, `BULK_DOCUMENT_DELETED` on Kafka.
- **`getAllDocumentEventsByCompanyId`**: Aggregation with filters (`is_archived`, `is_deleted`, `is_request_delete`, `is_duplicated`, etc.) and `$lookup` from `documentreadstatuses` for read state in list data.

### Schemas

- `src/schemas/document-detail-event.js` — `DocumentDetailEvent`: lifecycle flags (`is_archived`, `is_deleted`, `is_request_delete`, …), `hubdoc_data`, financial and reference fields.
- `src/schemas/document-read-status.js` — `DocumentReadStatus`: `document`, `user`, timestamps.
