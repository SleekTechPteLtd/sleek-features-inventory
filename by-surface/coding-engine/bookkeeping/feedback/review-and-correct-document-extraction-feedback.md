# Review and correct document extraction feedback

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Review and correct document extraction feedback |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Bookkeeper, Finance User |
| **Business Outcome** | Users can see ML extraction output stored per document and adjust feedback fields (including line items and category) during review before the document is published to the ledger. |
| **Entry Point / Surface** | Coding Engine API consumed by the Sleek bookkeeping / receipts document review experience (exact app navigation path not defined in this code). |
| **Short Description** | Authenticated callers fetch the ML feedback record for a document by document id, and update that feedback record by id with partial fields such as line items, category, and document event metadata so extraction can be corrected before publishing. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: ML/OpenAI extraction ingestion (`POST /feedback/extraction`, `POST /feedback/openai-extraction`, category-done flows) populates `mlfeedbackschemas` and sets status such as `TO_REVIEW`. Downstream: document publish and auto-publish logic in `DocumentService` and related flows when extraction processing completes. COA and supplier rules interact elsewhere in the same service during automated extraction, not in these two user-facing endpoints. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `mlfeedbackschemas` (MongoDB, `SLEEK_RECEIPTS` connection); reads/writes keyed by feedback `_id` (update) or `document_event` (get by document). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `PUT /feedback/:documentId` is named like a document id, but `FeedbackService.updateFeedbackById` updates by the ML feedback document’s MongoDB `_id`, not by `document_event`. Clients typically load feedback via `GET /feedback/document/:documentId` and must use the returned feedback `_id` for updates (or otherwise obtain that id). `req.user` is passed from `AuthGuard` but is not referenced inside `updateFeedbackById`—whether authorization is enforced only by guard or also by document/company checks should be confirmed. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Routes and auth** — `FeedbackController`: `GET feedback/document/:documentId` with `@UseGuards(AuthGuard)` calls `getFeedbackById` → `getFeedbackByDocumentId`. `PUT feedback/:documentId` with `@UseGuards(AuthGuard)` calls `updateFeedbackById` with `UpdateFeedbackDto` and `req.user` (`src/feedback/feedback.controller.ts`).
- **Fetch by document** — `getFeedbackByDocumentId` validates ObjectId, then `model.findOne({ document_event: new Types.ObjectId(documentId) })` (`src/feedback/feedback.service.ts`).
- **Update** — `updateFeedbackById` validates ObjectId and runs `model.updateOne({ _id: new Types.ObjectId(feedbackId) }, { $set: feedbackDetails })` (`src/feedback/feedback.service.ts`). Parameter name in service is `feedbackId` while the controller path param is named `documentId`.
- **DTO** — `UpdateFeedbackDto` allows optional `line_items`, `document_event_data`, `category` (`src/feedback/dto/feedback.dto.ts`).
- **Schema / collection** — `Feedback` maps to collection `mlfeedbackschemas`, with `document_event` ref to Document, extraction fields (`supplier`, amounts, `extractionData`, `status`, `category`, `similar_supplier_info`, etc.) (`src/feedback/models/feedback.schema.ts`).
- **Module** — `Feedback` model registered on `DBConnectionName.SLEEK_RECEIPTS` (`src/feedback/feedback.module.ts`).
