# Recover stuck receipt ML extraction

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Recover stuck receipt ML extraction |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, System (scheduled job or automation calling the endpoint or script) |
| **Business Outcome** | Stuck receipt documents leave the extraction backlog by either getting another ML pass or moving to manual verification, so bookkeeping data is not blocked indefinitely on failed extraction. |
| **Entry Point / Surface** | **Sleek Receipts service:** `POST /api/document-events/retrigger-v2` with `Authorization` matching `SLEEK_RECEIPTS_TOKEN` (same `validateDocumentEventAuth` as other document-event routes). **Batch script:** `src/scripts/retrigger-documents-to-ml.js` (connects MongoDB, calls `retriggerDocumentExtractionToMLV2` with fixed defaults). No app navigation path in this repo. |
| **Short Description** | Cursor-paginated batches requeue documents still in `EXTRACTING` to the ML extraction API (`getExtractionDataApi`) for submissions on or after the rolling two-day cutoff, and separately force-verify older stuck documents (submitted before that cutoff) by writing Coding Engine audit logs and setting status to `PROCESSING` (verify in UI). Batches pause 15 seconds between pages; overall caps per run via `maxLimit` and `maxDocumentLimit`. Optional filters: `startDate`, `endDate`, `companyId`. Toggle phases with `isRetriggerExtraction` and `isForceVerify`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** Receipt submission and initial `EXTRACTING` state. **External:** ML Node (`getExtractionDataApi` in `external-api/ml-node-server`); Coding Engine (`codingEngineCreateDocumentLogs` for force-verify path). **Related:** `POST /api/document-events/retrigger` (legacy `retriggerDocumentExtractionToML` per company/document filters). ML callbacks and category listeners (`ml-category-results-listener`, webhooks) apply extraction outcomes after requeue. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | Mongoose defaults: `documentdetailevents` (`DocumentDetailEvent` — `find`, `updateMany` on status for force verify). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether `fetchDocumentsToForceVerify` should select `company` for richer Coding Engine logs (controller only passes `_id` today). Exact scheduling/owner of the script vs API-only ops. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/scripts/retrigger-documents-to-ml.js`

- Bootstraps `dotenv-flow`, `databaseServer.connect()`, log4js to `./logs/retrigger-documents-to-ml.log`.
- Calls `DocumentEventService.retriggerDocumentExtractionToMLV2` with `maxLimit: 10`, `maxDocumentLimit: 500`, `isForceVerify: true`, `isRetriggerExtraction: true`.

### `src/services/document-event-service.js`

- **`retriggerDocumentExtractionToMLV2(options)`**: Parses `maxLimit`, `maxDocumentLimit`, `isForceVerify`, `isRetriggerExtraction`, `startDate`, `endDate`, `companyId`. Uses `twoDaysAgo = moment().subtract(2, "days").startOf("day")`.
- **`retrigger` branch** (`isRetriggerExtraction`): `fetchDocumentsToRetrigger` — `status: DOCUMENT_EVENT_STATUSES.EXTRACTING`, `submission_date: { $gte: date }`, cursor `_id` sort, `_id`/`file_uri`/`ledger`/`paid_by`/`company`; `retriggerExtractionProcess` → `getExtractionDataApi` with `DOCUMENT_TYPE.DOCUMENT_EVENT`.
- **`force verify` branch** (`isForceVerify`): `fetchDocumentsToForceVerify` — same `EXTRACTING` but `submission_date: { $lt: date }`; `updateDocumentStatusAndAddAuditLog` → `CODING_ENGINE_API.codingEngineCreateDocumentLogs` then `DocumentDetailEvent.updateMany` to `DOCUMENT_EVENT_STATUSES.PROCESSING` for successes.
- **`retriggerDocumentExtractionToML`**: Older targeted retrigger by company/document id (not the v2 batch script path).

### `src/routes/document-event.js`

- `router.post('/document-events/retrigger-v2', [validateDocumentEventAuth()], documentEventController.retriggerDocumentExtractionToMLV2)`.

### `src/controllers/document-event-controller.js`

- **`retriggerDocumentExtractionToMLV2`**: `options = get(req, "body", {})` passed through to service.

### `src/middleware/document-event-middleware.js`

- `validateDocumentEventAuth`: `req.headers.authorization === process.env.SLEEK_RECEIPTS_TOKEN` (pattern used across document-event tests).

### `src/schemas/document-detail-event.js`

- Model `DocumentDetailEvent` → collection `documentdetailevents`.
