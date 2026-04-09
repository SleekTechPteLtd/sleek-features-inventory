# Migrate document source to sleek-match

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Migrate document source to sleek-match |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (authenticated HTTP); operators running batch jobs (same service method is also exposed via Nest CLI `migrate-document-source` elsewhere in the repo) |
| **Business Outcome** | Documents tied to bank ledger transactions get `source: sleek-match`, consistent with sleek-match labelling so downstream behaviour and reporting stay aligned. |
| **Entry Point / Surface** | Coding Engine API: `POST /ledger-transactions/migrate-source-to-sleek-match` (OpenAPI tag `ledger-transaction`). Request body: optional `batchSize`, `dryRun` (default `true`), optional `companyId`. |
| **Short Description** | Scans ledger transactions that have a `document_id`, loads each document, and sets `source` to `sleek-match` when it is not already; supports batched paging, optional company filter, and dry-run (no writes). Returns success status, statistics, up to 100 sample migrated rows, and up to 50 error lines. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `DocumentService.getDocumentById` / `updateDocumentById`; `DocumentSource.SLEEK_MATCH`; ledger flows that attach documents to transactions; consumers of `document.source`. CLI command `migrate-document-source` delegates to the same service method. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `ledger_transactions` (read: transactions with non-null `document_id`; optional `company_id` filter); `documentdetailevents` (document `source` updates when not dry-run) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether production runs are primarily API vs CLI; whether default `dryRun: true` on the HTTP body surprises callers expecting live migration; market-specific rollout constraints unknown. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`ledger-transaction.controller.ts`:** `POST migrate-source-to-sleek-match`; `@UseGuards(AuthGuard, CompanyAccessGuard)`; `@ApiOperation` summary “Migrate document source to sleek-match” and description (ledger-uploaded documents, dry run preview); body `MigrateDocumentSourceDto`; destructures `batchSize = 100`, `dryRun = true`, optional `companyId`; calls `ledgerTransactionService.migrateDocumentSourceToSleekMatch`; wraps result in `MigrateDocumentSourceResponseDto` with `STATUS_RESPONSE.SUCCESS`, message reflecting dry-run vs live, `statistics`, `migratedDocuments`, optional `errorMessages`.

- **`ledger-transaction.service.ts`:**
  - `migrateDocumentSourceToSleekMatch(batchSize = 100, dryRun = true, companyId?)`: logs start; `buildMigrationQuery` → `document_id` `$ne` null and `$exists` true; optional `company_id` as `ObjectId`; `countDocuments`; paginated `find` with `skip`/`limit`, `select('ledger_transaction_id document_id')`, `lean`; per batch, parallel processing via `Promise.all` over `processSingleTransactionMigration`; `updateResultBasedOnProcessingStatus` / `handleTransactionProcessingError`; completion log; `InternalServerErrorException` on outer failure.
  - `processSingleTransactionMigration`: no `document_id` → `MigrationStatus.NO_DOCUMENT_ID`; `getDocumentById` → `NOT_FOUND` if missing; if `source === DocumentSource.SLEEK_MATCH` → `SKIPPED`; if not `dryRun`, `updateDocumentById` with `{ source: DocumentSource.SLEEK_MATCH }`; else returns `UPDATED` with `previousSource`.
  - `updateResultBasedOnProcessingStatus`: increments updated/skipped/not-found; pushes up to **100** samples for `UPDATED`.
  - `handleTransactionProcessingError`: increments `errors`; up to **50** `errorMessages`.

- **`dto/migrate-document-source.dto.ts`:** `MigrateDocumentSourceDto` — optional `batchSize` (min 1), `dryRun` (default true), `companyId`; Swagger on all. `MigrateDocumentSourceResponseDto` — `status`, `message`, `dryRun`, `statistics`, optional `migratedDocuments`, optional `errorMessages`; nested DTOs for statistics and migrated items (`previousSource`, `newSource` e.g. `sleek-match`).

- **Related (not in file list):** `MigrationStatus` from `commands/migrate-document-source/enum/migrate-document-source.enum`; collection names from `ledger-transaction.schema.ts` (`ledger_transactions`) and `document.schema.ts` (`documentdetailevents`).

- **Tests (contract):** `ledger-transaction.controller.spec.ts`, `ledger-transaction.service.spec.ts` (`migrateDocumentSourceToSleekMatch`).
