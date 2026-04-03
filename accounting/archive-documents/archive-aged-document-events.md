# Archive aged document events

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Archive aged document events |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Keeps day-to-day receipt and document work focused on recent submissions by soft-archiving document detail events older than one year, while preserving records and notifying downstream systems in bulk. |
| **Entry Point / Surface** | Operational batch script: `sleek-receipts` `src/scripts/archive-documents.js` (loads env, connects Mongo, selects candidates, calls archive). Same archive path is also reachable for authenticated bulk actions via `PUT /document-events/actions/archive` (controller → `archiveMultipleDocumentEventDetails`). |
| **Short Description** | A script finds all `DocumentDetailEvent` rows with `submission_date` at least one year ago, not deleted, and not already archived; it passes their IDs to `archiveMultipleDocumentEventDetails`, which sets `is_archived: true` in bulk and publishes a Kafka `BulkDocumentArchived` event with the ID list. Company receipt list APIs can filter by `isArchived` to separate active vs archived work. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Kafka (`KafkaService.publishEvent`, topic prefix `accounting-document-events`, type `BulkDocumentArchived`); `unarchiveMultipleDocumentEventDetails` / `BulkDocumentUnarchived` for reversal; `getAllDocumentEventsByCompanyId` optional `isArchived` filter; related manual/API bulk archive-unarchive on the same service methods |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `documentdetailevents` (read query in script; `updateMany` in `archiveMultipleDocumentEventDetails`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact schedule (cron/K8s) and environments where `archive-documents.js` runs are not defined in these files; whether one script run processes all matches in one batch or should be chunked for very large volumes. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Script (`src/scripts/archive-documents.js`)

- **`getDocumentEvents`:** `DocumentDetailEvent.find` with `submission_date <= now - 1 year`, `is_deleted` not true, `is_archived` not true; throws if none found.
- **`main`:** Maps `_id`s and calls `documentEventService.archiveMultipleDocumentEventDetails(ids)`.
- **Boot:** `dotenv-flow`, `databaseServer.connect()`, then runs `main`, logs timing, `process.exit`.

### Service (`src/services/document-event-service.js`)

- **`archiveMultipleDocumentEventDetails(ids)`:** Validates ObjectIds; `DocumentDetailEvent.updateMany` with `_id: { $in: ids }`, `$set: { is_archived: true }`; publishes `DocumentEventType.BULK_DOCUMENT_ARCHIVED` via `KafkaService.publishEvent` with `{ documentIds: ids, is_archived: true }`, `eventCaller: "document-event-service.archiveMultipleDocumentEventDetails"`.
- **`getAllDocumentEventsByCompanyId`:** Supports `isArchived` query string `'true'` / `'false'` to filter archived vs active lists (related UX for “recent” work).

### Schema (`src/schemas/document-detail-event.js`)

- **Model:** `DocumentDetailEvent`; field `is_archived: Boolean` among other receipt/document attributes.

### Kafka (`src/kafka/event.types.js`)

- **`DocumentEventType.BULK_DOCUMENT_ARCHIVED`:** `"BulkDocumentArchived"`; topic prefix `accounting-document-events`.

### HTTP (same capability surface, different entry)

- **`src/routes/document-event.js`:** `PUT /document-events/actions/archive` → `documentEventController.archiveMultipleDocumentEventDetails` (uses same service method as the script).
