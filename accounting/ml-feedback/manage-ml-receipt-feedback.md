# Manage ML receipt feedback

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage ML receipt feedback |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operations can submit receipt files for ML extraction, work through a searchable feedback queue, correct document fields and statuses, and retrieve human-readable file sources so receipt models can be trained and reviewed. |
| **Entry Point / Surface** | Sleek Receipts HTTP API under `/api/ml-feedback` (consumed by internal operations or tooling; exact app navigation not defined in these routes). |
| **Short Description** | Multipart upload creates `MLFeedback` records, stores files on S3, and triggers the ML extraction pipeline. List endpoints support paging, text search on submitter/status, filters for create type and auto-publish intent, and date ranges. Updates apply arbitrary document fields by feedback id. Readable-src returns a base64-encoded preview string for UI or review. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** `getExtractionDataApi` posts to ML Node Server (`/api/v1/sleek-ml`) in production/staging/SIT with S3 URI and `DOCUMENT_TYPE.ML_FEEDBACK`. **Downstream:** Webhook ingestion (`webhook-controller` / extraction callbacks) updates the same `MLFeedback` documents with extraction output and `TO_REVIEW` status. **Related:** `cloneDocumentEventToMLFeedback` links cloned queue items from `DocumentDetailEvent`; supplier rule creation may run on extraction webhooks. **Storage:** S3 via `FileUploader`. |
| **Service / Repository** | sleek-receipts; external ML Node Server (`ML_NODE_SERVER_BASE_URL`). |
| **DB - Collections** | `mlfeedbackschemas` (MongoDB, primary CRUD and aggregate); `documentdetailevents` (read/populate when listing ML feedback with `document_event` ref). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Routes register only `cors()` and `multipartHandler()`—no auth middleware appears on `ml-feedback` routes in `src/routes/ml-feedback.js`; whether callers are gated at gateway, network, or left open should be confirmed. `queryMLFeedback` returns only `result[0]` from the aggregation facet (first page metadata shape)—verify client expectations vs full `{ metadata, data }` structure. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Routes** — `src/routes/ml-feedback.js`: `POST /ml-feedback` (multipart), `GET /ml-feedback` (query), `GET /ml-feedback/readable-src/:documentId`, `PUT /ml-feedback/:documentId/details`; mounted under `/api` in `routes.js`.
- **Controller** — `src/controllers/ml-feedback-controller.js`: `createMLFeedback`, `updateMLFeedbackByDocumentId`, `queryMLFeedback`, `getMlFeedbackEventReadableSrcByDocumentId`; files from `req.files.files`.
- **Service** — `src/services/ml-feedback-service.js`: `createMLFeedback` (validate file, `MLFeedback.create`, S3 upload, `getExtractionDataApi`), `updateMLFeedbackByDocumentId` (`MLFeedback.updateOne` by `_id`), `queryDocuments` (aggregate with search/createType/autoPublishType/date filters, facet pagination, `DocumentDetailEvent.populate`), `getMLFeedbackReadableSrcByDocumentId` (`findById`, populate, `documentEventUtils.getReadableSrc` with `ML_FEEDBACK` source), `cloneDocumentEventToMLFeedback`.
- **Schema** — `src/schemas/ml-feedback.js`: model `MLFeedbackSchema`; fields include `document_event`, extraction and bookkeeping fields, `create_type`, `document` (file metadata), `quality`, `auto_publish`, `extractionData`, timestamps.
- **Constants** — `src/constants/ml-feedback-constants.js`: `ML_FEEDBACK_STATUSES` (done, processing, to_review), `CREATE_TYPES` (clone, create), `QUALITY_TYPES`, `AUTO_PUBLISH_TYPES`.
- **ML API** — `src/external-api/ml-node-server.js`: `getExtractionDataApi` POST to `${ML_NODE_SERVER_BASE_URL}/api/v1/sleek-ml` for non-local envs.
- **Readable source** — `src/utils/document-event-utils.js`: `getReadableSrc` loads S3 file, sets `readableSrc` via `fileUtils.encodeDocument`; for `ML_FEEDBACK` source returns the encoded string for the populated `document_event`.
