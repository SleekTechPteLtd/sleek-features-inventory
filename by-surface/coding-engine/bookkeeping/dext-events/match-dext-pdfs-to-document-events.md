# Match Dext PDFs to document events

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Match Dext PDFs to document events |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User; System (internal token–authenticated API and batch-style matching) |
| **Business Outcome** | For a company and date range, operators can see which Dext-sourced PDFs correspond to the same file already stored for internal document events, and successful pairs are linked so downstream extraction and status can align—unmatched items remain visible via returned failed/success lists. |
| **Entry Point / Surface** | Sleek Receipts REST API: `POST /dext-events/match` (body: `company`, `start_date`, `end_date`, `statuses`, optional `offset`, `limit`); guarded by shared `Authorization` token (`SLEEK_RECEIPTS_TOKEN`). No Sleek App navigation path is defined in these files. |
| **Short Description** | Resolves the company’s Dext account CRNs from settings, loads Dext events and internal document events in the window, downloads both sides’ PDFs from S3, and compares raw file buffers for equality. On a match, it records the pairing via document-event update logic (same path as other ML-similarity updates) and returns counts plus successful and failed URI pairs for reconciliation. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Company settings** (`dext_ids` links company to Dext account CRNs); **Dext event ingestion** (`POST /dext-events`, updates) feeding `DextEvent` with `file_uri`; **document events** (`DocumentDetailEvent`) in `PROCESSING` with receipt types filtered by ledger (SleekBooks vs Dext); **S3** (`FileUploader.getFileOnS3`) for byte comparison; **`documentEventService.updateDocumentEventDetailsByMLSimilarity`** when buffers match (updates Dext status to done and merges Dext metadata into the document event when conditions hold). |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `dextevents` (`DextEvent`: `account_crn`, `file_uri`, `status_v2`, `createdAt`, etc.); `companysettings` (`CompanySetting`: `company`, `dext_ids`); `documentdetailevents` (`DocumentDetailEvent`: `company`, `status`, `paid_by`, `file_uri`, date range, soft-delete/archive flags) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which operator-facing product or script calls `POST /dext-events/match`; whether byte-identical PDF comparison is sufficient for all real-world duplicates (vs perceptual hash); confirm market-specific expectations for Dext vs non–SleekBooks receipt type filters. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Routes (`src/routes/dext-event.js`)

- **`POST /dext-events/match`** — `validateDocumentEventAuth()`, `matchDextEvents`.
- Other routes on the same module: `POST /dext-events`, `GET /dext-events`, `PUT /dext-events/:externalId/details` (ingest/list/update Dext events).

### Controller (`src/controllers/dext-event-controller.js`)

- **`matchDextEvents`** — Reads `req.body` as `options`; delegates to `dextEventService.matchDextEvents`; success code `DEXT_EVENT_CODES.MATCH_DEXT_EVENTS`.

### Service (`src/services/dext-event-service.js`)

- **`matchDextEvents`** — Loads `CompanySetting.findOne({ company })`, reads `dext_ids` as Dext account CRNs; queries `DextEvent` where `account_crn` in those CRNs, `file_uri` present, `createdAt` within `[start_date, end_date]` (day boundaries via `moment`), `status_v2` in `statuses`; paginates with `skip`/`limit`. For each Dext event, loads document events via `getDocumentEventsByCompanyId(company, { start_date, end_date })`, builds URI lists, calls `comparePDFFiles(document_event_uris, dext_event_uris)`. Returns `{ allCount, updatedCount, options, failedMatches, successfulMatches }` (non-empty arrays only).

### Utils (`src/utils/dext-event-utils.js`)

- **`comparePDFFiles`** — For `s3://` URIs, parses bucket/path, fetches buffers with `FileUploader.getFileOnS3`, compares with strict equality (`dextBuffer === documentBuffer`). On match: splices URIs from working arrays, calls `documentEventService.updateDocumentEventDetailsByMLSimilarity({ [documentUri]: [dextUri] })`, pushes to `successMatch`; else pushes to `failedMatch`.
- **`getDocumentEventsByCompanyId`** — `DocumentDetailEvent.find` with `company`, `status: PROCESSING`, `paid_by` in receipt types from `checkCompanyByLedger` (SleekBooks → `ACCEPTED_RECEIPT_TYPES`, else `ACCEPTED_DEXT_RECEIPT_TYPES`), `file_uri` set, not deleted/archived, `createdAt` in range.

### Schema (`src/schemas/company-setting.js`)

- **`dext_ids`** — `String[]` associating the Mongo `company` with one or more Dext account CRNs used to filter `DextEvent.account_crn`.

### Related (not in file list but referenced)

- **`src/schemas/dext-event.js`** — `DextEvent` model fields including `external_id`, `account_crn`, `file_uri`, `status_v2`.
- **`src/middleware/document-event-middleware.js`** — `validateDocumentEventAuth`: requires `Authorization` header equal to `process.env.SLEEK_RECEIPTS_TOKEN`.
