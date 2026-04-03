# Apply ML extraction and image-similarity webhooks to documents

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Apply ML extraction and image-similarity webhooks to documents |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | ML extraction payloads and image-similarity results land in the same data the product uses for receipts, so feedback records and document events stay aligned with what the ML pipeline extracted and which historical Dext documents matched. |
| **Entry Point / Surface** | System: HTTP `POST /webhook/ml-extraction` and `POST /webhook/ml-image-similarity` on sleek-receipts (shared-token auth via `Authorization` header) |
| **Short Description** | The ML server posts extraction results keyed by ML feedback id or document event id; the service normalizes fields (including optional MLBK v2 shaping), may create missing suppliers from rules, updates `MLFeedback` to review status, and for document-event callbacks also refreshes linked ML feedback and, when still extracting, merges supplier/totals/dates into the `DocumentDetailEvent`. A separate webhook applies image-similarity maps (document S3 URI → Dext URI) to copy Dext line detail onto extracting documents and mark matched Dext events done. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: ML extraction service / image-similarity service (HTTP callbacks). Outbound from related flows: `getExtractionDataApi` (ml-node-server) when documents are first sent for extraction. Downstream: supplier rules API (`supplierRuleServiceCreateSupplierIfDoesNotExists`), bookkeeping UIs and flows that read `documentdetailevents` / ML feedback. Related: ERPNext and Zoho webhook handlers in the same controller are separate capabilities. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `mlfeedbackschemas`, `documentdetailevents`, `dextevents` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/routes/webhook.js`** — `POST /ml-extraction` → `WebhookController.receiveExtractionData`; `POST /ml-image-similarity` → `receiveImageSimilarityData`; both wrapped with `validateDocumentEventAuth()` (token must equal `process.env.SLEEK_RECEIPTS_TOKEN`).
- **`src/middleware/document-event-middleware.js`** — `validateDocumentEventAuth`: compares `req.headers.authorization` to `SLEEK_RECEIPTS_TOKEN`.
- **`src/controllers/webhook-controller.js`** — `receiveExtractionData`: reads `body.id`, `body.type`, `body.data`; optional `MLBK_FORMAT_V2_ENABLED` → `formatMLBK` / `filterFalsy` / `formatDate` / `validateAutoPublish`; on `ML_FEEDBACK` type calls `mlFeedbackService.updateMLFeedbackByDocumentId(id, documentDetails)` with status `TO_REVIEW`; on `DOCUMENT_EVENT` loads `MLFeedback` by `document_event: id` and `DocumentEvent` by id, updates linked ML feedback when present, and if document status is `EXTRACTING` calls `documentEventService.updateDocumentEventDetailsByDocumentId` with supplier/total/date/currency plus optional `customer` for sales-invoice ledger. `receiveImageSimilarityData` delegates to `documentEventService.updateDocumentEventDetailsByMLSimilarity(body)`.
- **`src/services/ml-feedback-service.js`** — `updateMLFeedbackByDocumentId`: `MLFeedback.updateOne` by `_id` with `$set` of merged extraction payload and status; used by webhook path. (Also `createMLFeedback`, `cloneDocumentEventToMLFeedback`, `getExtractionDataApi` for outbound ML requests.)
- **`src/services/document-event-service.js`** — `updateDocumentEventDetailsByDocumentId`: validates ObjectId, `computeDocumentEventDetails`, duplicate check, `DocumentDetailEvent.updateOne`. `updateDocumentEventDetailsByMLSimilarity`: iterates `mlDetails` map (document file URI → array of Dext URIs); skips unless exactly one match; loads `DextEvent` by `file_uri`, updates Dext `status_v2` to done, finds `DocumentDetailEvent` by `file_uri` + `EXTRACTING`, builds field payload from Dext (amounts, dates, supplier, category, customer, etc.), applies expense-claim vs in-books status rules, calls `updateDocumentEventDetailsByDocumentId`.
- **`src/schemas/ml-feedback.js`**, **`src/schemas/document-detail-event.js`**, **`src/schemas/dext-event.js`** — Mongoose models backing the collections above.
