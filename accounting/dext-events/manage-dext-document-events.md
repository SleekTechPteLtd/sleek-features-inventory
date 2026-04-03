# Manage Dext document events

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage Dext document events |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (authenticated backend clients: Dext pipeline, robots, internal services — not end-user UI) |
| **Business Outcome** | Receipt and invoice metadata from Dext stays stored in Sleek’s data model and, when a Dext row is re-synced and already exists, linked in-app document records stay aligned with Dext so bookkeeping views and downstream flows reflect the same figures and references. |
| **Entry Point / Surface** | sleek-receipts HTTP API: `POST/GET /dext-events`, `PUT /dext-events/:externalId/details`, `POST /dext-events/match` (all behind `validateDocumentEventAuth` / `Authorization: SLEEK_RECEIPTS_TOKEN`) |
| **Short Description** | Ingests Dext payloads (create or upsert by Dext `id` as `external_id`), lists Dext events with filters and paginated aggregation, updates a Dext event by external id, and supports an optional batch “match” pass that compares PDFs between Dext events and company document events. When ingest finds an existing `external_id`, it updates the Dext row and pushes mapped fields into any linked `DocumentDetailEvent` via `dext_event` reference. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Dext as source of document metadata; `document-event-service` for linked `DocumentDetailEvent` updates (`updateDocumentEventByDextEventId`) and readable file resolution by Dext `external_id`; `company-setting` for company `dext_ids` (CRNs) used in match; `dext-event-utils` (`getDocumentEventsByCompanyId`, `comparePDFFiles`) for manual/ops matching; ML similarity flow elsewhere updates Dext status and document events (`updateDocumentEventDetailsByMLSimilarity`). |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `dextevents` (DextEvent model), `companysettings` (CompanySetting in match flow), `documentdetailevents` (DocumentDetailEvent when syncing from create path or match utilities) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `PUT /dext-events/:externalId/details` updates only `DextEvent` and does not call `updateDocumentEventByDextEventId`; propagation to linked document events occurs on the create/upsert path when `createDextEvent` finds an existing `external_id`. Confirm whether callers rely on PUT for reconciliation or always use POST for full sync. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Routes and auth (`src/routes/dext-event.js`, `src/middleware/document-event-middleware.js`)

- `POST /dext-events` → `createDextEvent` — shared secret: header `Authorization` must equal `process.env.SLEEK_RECEIPTS_TOKEN`.
- `GET /dext-events` → `getDextEvents` — same guard.
- `PUT /dext-events/:externalId/details` → `updateDextEventByExternalId` — same guard.
- `POST /dext-events/match` → `matchDextEvents` — same guard.

### Controller (`src/controllers/dext-event-controller.js`)

- `createDextEvent`, `getDextEvents`, `updateDextEventByExternalId`, `matchDextEvents` delegate to `dext-event-service`.

### Service — ingest and list (`src/services/dext-event-service.js`)

- **`createDextEvent`**: Maps Dext payload fields to schema (`external_id` from `id`, amounts, dates, supplier, `file_uri`, etc.). If no document exists for `external_id`, creates with `status_v2: PROCESSING`. If one exists, `$set` updates the row and calls `documentEventService.updateDocumentEventByDextEventId(dextEvent._id, dextDetails)` so linked document events stay aligned.
- **`getDextEvents`**: Aggregation pipeline with optional `$match` on `status_v2` (comma-separated `statuses`), `external_id`, `_id` (`documentId`), `account_crn`; `$facet` for total count and paginated data (`skip`, `limit`, default limit 10); sort by `createdAt` (`sortOrder`).
- **`updateDextEventByExternalId`**: `DextEvent.updateOne({ external_id }, { $set: dextEventDetails })` — no document-event propagation in this function.
- **`matchDextEvents`**: Loads `CompanySetting` by `company`, reads `dext_ids`; finds `DextEvent` rows in date/status range with `file_uri`; for each, loads document events via `getDocumentEventsByCompanyId` and `comparePDFFiles` to attempt PDF matching (operational pairing, not the main ingest path).

### Schema (`src/schemas/dext-event.js`)

- Mongoose model `DextEvent`: fields include `external_id`, `account_crn`, document and amount fields, `file_uri`, `status_v2`, `timestamps`.

### Linked document updates (`src/services/document-event-service.js`)

- **`updateDocumentEventByDextEventId`**: Finds `DocumentDetailEvent` with `dext_event` equal to the Dext row id; maps Dext fields into document event (amounts, supplier, category from `category_name`, expense-claim vs in-books status rules, archived/expense-report gating for expense claims).
- **`getDocumentEventReadableSrcByExtractionId`**: For `extractionType` dext, resolves `DextEvent` by `external_id` to load file content.
- **`updateDocumentEventByExtractionId`**: Finds Dext by `extraction_id`, then document by `dext_event` — related path for invoice-style updates from elsewhere.

### Constants touched

- `DEXT_EVENT_STATUSES` from `constants/dext-event-constants` (create uses `PROCESSING`; ML similarity flow sets `DONE` elsewhere in this service file).
