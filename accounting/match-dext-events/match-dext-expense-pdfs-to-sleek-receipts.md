# Match Dext expense PDFs to Sleek receipts

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Match Dext expense PDFs to Sleek receipts |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Pending Dext expense documents and in-app receipt documents that represent the same PDF are linked so Dext extraction and Sleek bookkeeping stay aligned for the same underlying file. |
| **Entry Point / Surface** | Batch job (`node` script after DB connect); no Sleek App navigation. Intended to run on a schedule or operator invocation against MongoDB and S3. |
| **Short Description** | For up to five companies at a time, loads Dext events in `PROCESSING` with a file URI and retry under five, resolves the company via `CompanySetting.dext_ids`, loads matching `DocumentDetailEvent` rows on the same calendar days (by `createdAt` on the Dext side), keeps only `.pdf` URIs, downloads both sides from S3, and when a pair compares equal it calls `updateDocumentEventDetailsByMLSimilarity` to attach the Dext payload and mark the Dext event done. Increments `retry` on each processed Dext event. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Company settings** (`dext_ids` ↔ Dext `account_crn`); **Dext ingestion** populating `DextEvent` with `file_uri` and `status_v2`; **document submission** creating `DocumentDetailEvent` with `file_uri` and `PROCESSING` status; **AWS S3** via `FileUploader.getFileOnS3`; **ledger-aware receipt types** (`checkCompanyByLedger` / ERP Next vs Dext sets from receipt constants). Related: on-demand matching via `POST /dext-events/match` and `dextEventService.matchDextEvents` (separate code path). |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `dextevents` (`DextEvent`); `documentdetailevents` (`DocumentDetailEvent`); `companysettings` (`CompanySetting` for `company`, `dext_ids`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Cron or orchestration that runs `src/scripts/match-dext-events.js` is not defined in these files; comment mentions reset behaviour when retry reaches five but reset logic is not shown in this script; confirm production expectations for PDF byte comparison vs the shared `FileUploader` implementation. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Script (`src/scripts/match-dext-events.js`)

- **`getDextEvents`** — `DextEvent.aggregate`: `status_v2: PROCESSING`, `retry < 5`, `file_uri` present; groups by `account_crn`; slices up to 10 events per company; `$limit` 5 companies.
- **`getDocumentEventsByCompanyId`** — `DocumentDetailEvent.aggregate` for `company`, `status: PROCESSING`, `paid_by` in ledger-dependent receipt types (`ACCEPTED_RECEIPT_TYPES` vs `ACCEPTED_DEXT_RECEIPT_TYPES`), `file_uri` set, not deleted/archived; `createdAt` filtered to the same calendar days as the batch’s Dext `createdAt` values (`$or` of day ranges).
- **`formatPDFDetails`** — Restricts to URIs ending in `.pdf`.
- **`comparePDFFiles`** — For `s3://` URIs, parses bucket and key, fetches via `FileUploader.getFileOnS3`, on “match” calls `documentEventService.updateDocumentEventDetailsByMLSimilarity({ [documentEventImage]: [dextEventImage] })`, splices matched URIs from working arrays, logs counts.
- **`updateDextEventRetry`** — Increments `retry` per Dext event id after each company batch.
- **`main`** — Resolves `CompanySetting.find({ dext_ids: { $in: [account_crn] } })`, runs comparison when both sides have PDFs, logs when no company or no document events.

### Service (`src/services/document-event-service.js`)

- **`updateDocumentEventDetailsByMLSimilarity`** — Loads `DextEvent` by `file_uri`, sets `status_v2` to `DEXT_EVENT_STATUSES.DONE`, maps Dext financial and metadata fields onto `DocumentDetailEvent` (including `dext_event` reference), applies expense-claim vs in-books status rules using `is_archived` / `in_expense_report`, calls `updateDocumentEventDetailsByDocumentId` for the linked document.

### Schemas

- **`src/schemas/dext-event.js`** — `DextEvent`: `account_crn`, `file_uri`, `retry`, `status_v2`, extracted amounts, supplier, etc.
- **`src/schemas/document-detail-event.js`** — `DocumentDetailEvent`: `company`, `file_uri`, `status`, `paid_by`, `dext_event` ObjectId ref, timestamps (`createdAt` used in queries).

### Constants (`src/constants/dext-event-constants.js`)

- **`DEXT_EVENT_STATUSES`** — `DONE`, `PROCESSING` (script matches only `PROCESSING`; service sets `DONE` after link).
