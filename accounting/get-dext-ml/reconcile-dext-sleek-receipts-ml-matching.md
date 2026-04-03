# Reconcile Dext events with Sleek receipts via ML matching

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Reconcile Dext events with Sleek receipts via ML matching |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Dext-ingested documents and Sleek-submitted receipts for the same company stay linked to one logical file, so extracted Dext data can populate the correct Sleek document event without manual pairing. |
| **Entry Point / Surface** | Background: batch script `src/scripts/get-dext-ml.js` (connects MongoDB, processes queued `DextEvent` rows). Image matches are completed when the ML service posts results to the existing image-similarity webhook (see `accounting/webhook/integrate-ml-extraction-and-similarity-callbacks.md`). Not an end-user screen. |
| **Short Description** | The job loads Dext events in `PROCESSING` with `file_uri`, groups them by `account_crn`, finds matching `DocumentDetailEvent` rows (same `dext_account_crn`, Dext-capable `paid_by`, `PROCESSING`, with `file_uri`). Non-PDF pairs are sent to the ML node server `compare-images` API; PDF pairs are compared by loading both objects from S3 and, when buffers match, linkage is updated immediately via `updateDocumentEventDetailsByMLSimilarity`. Retry/reset counters on Dext events throttle repeated work. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** Dext pipeline populates `dextevents`; users/companies submit receipts that create `documentdetailevents` with `dext_account_crn`. **Outbound:** `ML_NODE_SERVER_BASE_URL` — `POST /api/v1/sleek-ml/compare-images` (production, staging, SIT only). **Completes image path:** ML service callback → `receiveImageSimilarityData` → `updateDocumentEventDetailsByMLSimilarity` (documented under webhook feature). **Related:** `match-dext-events` script, Dext extraction/update flows, `getExtractionDataApi` for extraction (separate from compare-images). |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `dextevents`, `documentdetailevents` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Script comments reference legacy “ml-image-similarity (DISCONTINUED)” for images; confirm operational ownership of compare-images + webhook in each environment. PDF branch compares S3 object bodies after UTF-8 string conversion — confirm this matches intended binary-equality semantics for all PDFs. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/scripts/get-dext-ml.js`** — `main()`: queries `DextEvent` with `status_v2: PROCESSING`, `retry < 5`, `file_uri` set, reset guard; batches limit 10; `findDuplicates` / `formatDextDetails` by `account_crn`; `DocumentDetailEvent.find` with `status: PROCESSING`, `paid_by` in `ACCEPTED_DEXT_RECEIPT_TYPES`, matching `dext_account_crn`; splits URIs into PDF vs image; `formatMLDetails` builds `mlParams` (`hash_size: 16`, `sleek_images`, `dext_images`) and `pdfParams`; calls `ml_node_server.compareImageSimilarityApi(mlParams)` when both sides have non-PDF URIs; `comparePdfFiles` uses `FileUploader.getFileOnS3` and on equality calls `documentEventService.updateDocumentEventDetailsByMLSimilarity({ [sleekImage]: [dextImage] })`; increments `retry` on processed Dext rows; when no work, resets `retry` and increments `reset` for stuck rows (max reset 1). Entrypoint: `databaseServer.connect()`, then `main()`.
- **`src/external-api/ml-node-server.js`** — `compareImageSimilarityApi`: `POST ${ML_NODE_SERVER_BASE_URL}/api/v1/sleek-ml/compare-images`; no-op in non–production/staging/SIT environments (returns without calling).
- **`src/services/document-event-service.js`** — `updateDocumentEventDetailsByMLSimilarity(mlDetails)`: expects map of document `file_uri` → single Dext `file_uri`; loads `DextEvent` by `file_uri`, sets `status_v2` to `DONE`, merges Dext fields into `DocumentDetailEvent` in `EXTRACTING` (supplier, amounts, dates, `dext_event` link, status rules for expense claims vs in-books); uses `updateDocumentEventDetailsByDocumentId`. Exported for script and webhook.
- **`src/schemas/dext-event.js`** — Model `DextEvent`: fields include `account_crn`, `file_uri`, `retry`, `reset`, `status_v2`, extraction/business fields.
- **`src/schemas/document-detail-event.js`** — Model `DocumentDetailEvent`: `dext_account_crn`, `file_uri`, `status`, `dext_event` ObjectId ref, receipt metadata.
- **`src/files/uploader.js`** — `getFileOnS3(path, bucket, false)` returns UTF-8 string body for S3 `getObject` (used in PDF comparison path).
