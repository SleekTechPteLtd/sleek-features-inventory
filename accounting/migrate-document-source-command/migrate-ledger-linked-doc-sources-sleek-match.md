# Migrate ledger-linked document sources to sleek-match

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Migrate ledger-linked document sources to sleek-match |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (CLI); authenticated app users with company access (HTTP API) |
| **Business Outcome** | Documents linked from bank ledger transactions carry `source: sleek-match`, matching how matching flow labels them today so downstream behavior and reporting stay consistent. |
| **Entry Point / Surface** | Operations: Nest CLI command `migrate-document-source.command` (`--batchSize`, `--dryRun`, `--companyId`). API: `POST /ledger-transactions/migrate-source-to-sleek-match` (OpenAPI `LedgerTransactionController_migrateDocumentSourceToSleekMatch`). |
| **Short Description** | Finds ledger transactions that reference a `document_id`, loads each document, and sets `source` to `sleek-match` when it is not already; supports batched processing, optional dry-run (no writes), and optional company scope. The same migration runs from the CLI or the authenticated controller. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `DocumentService.getDocumentById` / `updateDocumentById`; `DocumentSource.SLEEK_MATCH` (`document.enum.ts`); ledger–document reconciliation flows that attach `document_id` to transactions; any consumers of `document.source` |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `ledger_transactions` (query: `document_id` present and non-null; optional `company_id`); `documentdetailevents` (document `source` updates) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether production runs are intended primarily via CLI vs API; whether a global rollout needs scheduling or throttling beyond batch size; default `dryRun: true` on HTTP body may surprise callers expecting live migration. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **CLI — `migrate-document-source.command.ts`:** Nest Commander `migrate-document-source.command`; description states migration of document `source` to sleek-match for documents uploaded through ledger transactions. Options: `--batchSize` (default 100, min 1, max 500), `--dryRun` (preview, no DB updates), `--companyId` (optional filter). Delegates to `LedgerTransactionService.migrateDocumentSourceToSleekMatch(batchSize, isDryRun, companyId)`; logs counts (updated/skipped/not found/errors), sample migrated rows, and `errorMessages`; exits `0`/`1`.

- **Service — `ledger-transaction.service.ts`:**
  - `migrateDocumentSourceToSleekMatch(batchSize = 100, dryRun = true, companyId?)`: builds query via `buildMigrationQuery` (`document_id` `$ne` null and `$exists` true; optional `company_id` as `ObjectId`); `countDocuments` / paginated `find` with `skip`/`limit` on `ledger_transaction_id` + `document_id`; per-transaction `processSingleTransactionMigration`.
  - `processSingleTransactionMigration`: `documentService.getDocumentById`; skip if `source === DocumentSource.SLEEK_MATCH`; if not `dryRun`, `documentService.updateDocumentById` with `{ source: DocumentSource.SLEEK_MATCH }`; statuses `UPDATED` / `SKIPPED` / `NOT_FOUND` / `NO_DOCUMENT_ID` (`MigrationStatus` enum).
  - Result aggregation: `updateResultBasedOnProcessingStatus` pushes up to **100** sample items into `migratedDocuments`; `handleTransactionProcessingError` caps `errorMessages` at **50** entries.
  - Batches use `Promise.all` over transactions with per-item catch into `handleTransactionProcessingError`.

- **HTTP — `ledger-transaction.controller.ts`:** `POST ledger-transactions/migrate-source-to-sleek-match`; `@UseGuards(AuthGuard, CompanyAccessGuard)`; body `MigrateDocumentSourceDto` (`batchSize`, `dryRun` default **true**, `companyId`); `@ApiOperation` summary/description for migration and dry-run preview; returns `MigrateDocumentSourceResponseDto` with `STATUS_RESPONSE.SUCCESS`, statistics, `migratedDocuments`, optional `errorMessages`.

- **DTOs / types:** `ledger-transaction/dto/migrate-document-source.dto.ts` (Swagger for API); `commands/migrate-document-source/types/migrate-document-source.types.ts` (`MigrateDocumentSourceOptions`, result shapes).

- **Schemas:** `ledger-transaction.schema.ts` — collection `ledger_transactions`; `document.schema.ts` — collection `documentdetailevents`; `DocumentSource.SLEEK_MATCH = 'sleek-match'` in `document.enum.ts`.

- **Tests (behavior contract):** `migrate-document-source.command.spec.ts`, `ledger-transaction.service.spec.ts` (`describe('migrateDocumentSourceToSleekMatch')`), `ledger-transaction.controller.spec.ts` (`migrateDocumentSourceToSleekMatch`).
