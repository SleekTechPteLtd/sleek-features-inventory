# Retry document extraction for bookkeeping

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Retry document extraction for bookkeeping |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | When ML extraction stalls or needs another pass, operators can re-send documents to the extraction service so line items, suppliers, and amounts can be captured into the bookkeeping flow. |
| **Entry Point / Surface** | Sleek Receipts service HTTP API: `POST /document-events/retrigger` (body: `company._id` and/or `document._id`, optional `statuses`, `startDate`, `endDate`, `skip`, `limit`) and `POST /document-events/retrigger-v2` (batch options: `isRetriggerExtraction`, `isForceVerify`, `maxLimit`, `maxDocumentLimit`, `startDate`, `endDate`, `companyId`). Both require `Authorization` matching `SLEEK_RECEIPTS_TOKEN`; no end-user app path is defined in this repo. Service comment notes V2 is used from **sleek-robot**; `src/scripts/retrigger-documents-to-ml.js` calls `retriggerDocumentExtractionToMLV2`. |
| **Short Description** | **V1 (`retriggerDocumentExtractionToML`):** Loads `DocumentDetailEvent` rows by company filters or a single `document._id`, then for each document calls `getExtractionDataApi` with the document id, S3 `file_uri`, ledger, receipt type, and company — the same ML entrypoint used at ingest — so the ML pipeline runs again. **V2:** Cursor-based batching finds documents stuck in `extracting` (retrigger path) or applies “force verify” for older stuck docs: logs to the coding engine, then sets status to `processing` for successfully logged ids. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **ML:** `getExtractionDataApi` (`src/external-api/ml-node-server.js`) POSTs to `${ML_NODE_SERVER_BASE_URL}/api/v1/sleek-ml` in `production` / `staging` / `sit`; no request in default (local) `NODE_ENV`. **Downstream:** ML/webhook callbacks apply extraction to documents (see related `webhook` inventory entries). **V2 force-verify:** `CODING_ENGINE_API.codingEngineCreateDocumentLogs` then `DocumentDetailEvent.updateMany` to `PROCESSING`. **Initial ingest parity:** Same `getExtractionDataApi` payload shape as `createDocumentEvent` (with optional `env` on first-time ingest only). |
| **Service / Repository** | sleek-receipts; callers include sleek-robot (V2) per code comment |
| **DB - Collections** | `documentdetailevents` (`DocumentDetailEvent` — read for retrigger selection; V2 `updateMany` / `find` for batch and force-verify). No writes on the V1 happy path beyond reads. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | V1 `retriggerDocumentExtractionToML` pushes the result of `getAllDocumentEventsByCompanyId` (aggregation shape with `data` / `metadata`) into an array treated like individual documents, and the loop contains an early `return` after the first iteration — behavior for multi-document company retrigger may not match intent; confirm with runtime usage. Which markets or tenants rely on retrigger vs resubmission (`receipts-resubmission`) for recovery. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/routes/document-event.js`

- `POST /document-events/retrigger` → `documentEventController.retriggerDocumentExtractionToML`, middleware `validateDocumentEventAuth()`.
- `POST /document-events/retrigger-v2` → `documentEventController.retriggerDocumentExtractionToMLV2`, same auth.

### `src/middleware/document-event-middleware.js`

- `validateDocumentEventAuth`: `req.headers.authorization === process.env.SLEEK_RECEIPTS_TOKEN`.

### `src/controllers/document-event-controller.js`

- `retriggerDocumentExtractionToML`: body → `documentEventService.retriggerDocumentExtractionToML`; success via `SUCCESS_CODES.DOCUMENT_EVENT_CODES.RETRIGGER_DOCUMENT_EXTRACTION` (`RETRIGGER_DOCUMENT_EXTRACTION`).
- `retriggerDocumentExtractionToMLV2`: body → `retriggerDocumentExtractionToMLV2`.

### `src/services/document-event-service.js`

- **`retriggerDocumentExtractionToML`:** Resolves candidates via `company._id` → `getAllDocumentEventsByCompanyId` or `document._id` → `getDocumentEventByDocumentId`; iterates and calls `getExtractionDataApi({ id, type: DOCUMENT_TYPE.DOCUMENT_EVENT, s3_uri: fileUri, ledger, receipt_type: paid_by, company_id })`; accumulates `success_ids` / `failed_ids`.
- **`retriggerDocumentExtractionToMLV2`:** If `isRetriggerExtraction`, loops with `fetchDocumentsToRetrigger` (status `EXTRACTING`, submission after configurable window, optional company/date) → `retriggerExtractionProcess` → `getExtractionDataApi` per doc. If `isForceVerify`, `fetchDocumentsToForceVerify` (older `EXTRACTING`) → `updateDocumentStatusAndAddAuditLog` (coding engine logs + `DocumentDetailEvent.updateMany` to `PROCESSING`).
- **`retriggerExtractionProcess` / `fetchDocumentsToRetrigger`:** `DocumentDetailEvent.find` with selected fields.

### `src/external-api/ml-node-server.js`

- **`getExtractionDataApi`:** Axios POST to ML sleek-ml endpoint; environments listed above.

### `src/constants/success-message.js`

- `DOCUMENT_EVENT_CODES.RETRIGGER_DOCUMENT_EXTRACTION`: message *Sucessfully attempted to retrigger document extraction.*

### `src/constants/webhook-constants.js`

- `DOCUMENT_TYPE.DOCUMENT_EVENT` used as ML payload `type`.

### `src/schemas/document-detail-event.js`

- Mongoose model `DocumentDetailEvent` (collection name follows Mongoose default for that model).

### `src/scripts/retrigger-documents-to-ml.js`

- Invokes `retriggerDocumentExtractionToMLV2` with CLI-derived options (operational batch entry point in-repo).
