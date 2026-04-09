# Soft-delete document events by company

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Soft-delete document events by company |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Selected companies’ receipt document detail events are excluded from active processing and default “non-deleted” views while rows stay in the database for audit and recovery options. |
| **Entry Point / Surface** | `sleek-receipts` operational script: run Node against `src/scripts/soft-delete-documents.js` with a comma-separated list of company MongoDB ObjectIds (argv[2]). Connects via `database/server` after `dotenv-flow` config. Not exposed through the Sleek app or a public HTTP route. |
| **Short Description** | Bulk `updateMany` on the `DocumentDetailEvent` model sets `is_deleted: true` for every document event whose `company` field is in the supplied ID list. Validates IDs before running. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Downstream behaviour:** Listing and pipelines that treat “active” receipts as `is_deleted` in `[false, null]` (e.g. `document-event-service` aggregation when filtering non-deleted; `receipts-resubmission.service`, `match-dext-events`, `get-xero-client-invoices` scripts; `external-requests` routes using `is_deleted: { $ne: true }`). **Kafka:** `event.util.js` maps `is_deleted` / `is_archived` onto outbound accounting document payloads. **Schema:** `document-detail-event` defines `is_deleted` as a Boolean alongside lifecycle flags (`is_archived`, `is_duplicated`, etc.). |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | MongoDB collection backing Mongoose model `DocumentDetailEvent` (default pluralized name `documentdetailevents`) — `updateMany` with `$set: { is_deleted: true }` where `company` `$in` provided ObjectIds |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether runbooks or automation wrap this script in any environment; `document-event-service` is imported in the script but unused (dead import). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Script** — `src/scripts/soft-delete-documents.js`: `validateArguments` splits comma-separated company IDs, checks non-empty list and `ObjectId.isValid` for each; `updateOperation` calls `DocumentDetailEvent.updateMany({ company: { $in: ids } }, { $set: { is_deleted: true } })`; `main` wraps `updateOperation`; top-level IIFE connects via `databaseServer.connect()`, logs timing and Mongo update result, `process.exit()`. Imports `document-event-service` but does not call it.
- **Schema** — `src/schemas/document-detail-event.js`: Mongoose schema includes `company` (required ObjectId), `is_deleted: Boolean`, `is_archived`, `is_duplicated`, `is_request_delete`, `delete_request`, financial and metadata fields; `pre('updateMany')` hook for `currency_rate` normalization only.
- **Active-processing filters** — `src/services/document-event-service.js` (non-deleted facet): `$match: { is_deleted: { $in: [false, null] } }` when `isDeleted === 'false'`.
- **Other readers** — `src/services/receipts-resubmission.service.js`, `src/utils/dext-event-utils.js`, `src/scripts/match-dext-events.js`, `src/scripts/get-xero-client-invoices.js`: queries include `is_deleted: { $in: [false, null] }` or equivalent; `src/routes/external-requests.js`: `is_deleted: { $ne: true }`.
- **Kafka** — `src/kafka/event.util.js`: when `is_deleted` or `is_archived` is present on the document, payload sets `is_deleted: document.is_deleted || document.is_archived`.
