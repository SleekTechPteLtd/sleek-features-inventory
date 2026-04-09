# Track and resolve missing receipt gaps

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Track and resolve missing receipt gaps |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Bookkeeper; System (ingestion) |
| **Business Outcome** | Bookkeeping can see which bank-side transactions still lack a supporting receipt, work through the backlog, and close items when receipts are linked so the audit trail stays complete. |
| **Entry Point / Surface** | Sleek App > Bookkeeping > Receipts (missing-documents backlog); API routes in sleek-receipts protected by service token |
| **Short Description** | Records missing-document rows per company (from upstream bookkeeping), lists open items (status not `done`) with pagination, text search on description and amounts, and optional transaction date range. Users clear the “new” flag after review and mark items complete when document event IDs are attached. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Sleek Back API (`getCompanyDetailsByCompanyName`) to resolve `company` ObjectId on create; `DocumentDetailEvent` references on link; `comments-service` loads missing documents by id for comments on missing documents |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `missingdocuments` (Mongoose model `MissingDocument`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Exact in-app navigation label for the backlog; whether all client traffic uses the same `SLEEK_RECEIPTS_TOKEN` pattern or a gateway adds user context |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Routes** (`src/routes/missing-document.js`): `POST /missing-documents` (create batch); `GET /missing-documents/companies/:companyId` (list); `PUT /missing-documents/:missingDocumentId/new` (clear `is_new`); `PUT /missing-documents/update-status/:missingDocumentId` (complete + link events). All use `validateDocumentEventAuth()` — `Authorization` header must equal `process.env.SLEEK_RECEIPTS_TOKEN`.
- **Controller** (`src/controllers/missing-document-controller.js`): `createMissingDocument`, `getAllMissingDocumentsByCompanyId`, `updateNewFlagByMissingDocumentId`, `updateMissingDocumentStatus` → service layer.
- **Service** (`src/services/missing-document-service.js`): `createMissingDocument` loops payload, resolves company via `SLEEK_BACK_API.getCompanyDetailsByCompanyName`, `MissingDocument.create`. `getAllMissingDocumentsByCompanyId` aggregates with `$match` company + `status` ≠ `"done"`, optional `$regex` search on `transaction_description` / string forms of `spent`/`received`, optional `transaction_date` range via `startDate`/`endDate`, `$facet` for total count + sorted paginated data. `updateNewFlagByMissingDocumentId` sets `is_new: false`. `updateMissingDocumentStatusById` sets `status: "done"` and `$addToSet` on `document_events` from `missingDocumentDetails.ids`. Exported `getMissingDocumentById` used elsewhere (e.g. comments).
- **Schema** (`src/schemas/missing-document.js`): `company`, `company_name`, `bank_account`, `spent`, `received`, `transaction_description`, `transaction_date`, `is_new` (default `true`), `document_events` → `DocumentDetailEvent`, `status`, timestamps.
- **Tests** (`src/tests/controllers/missing-document-controller.js`): skipped suite shows `PUT .../update-status/...` body `{ ids: [ObjectId strings] }`.
