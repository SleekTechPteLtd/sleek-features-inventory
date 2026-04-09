# Bulk archive documents from a Google Sheet

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Bulk archive documents from a Google Sheet |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (CLI / scheduled jobs); System (Kubernetes CronJobs) |
| **Business Outcome** | Archives many accounting documents in one run so their archived state matches lists curated in Google Sheets (per tab or every tab), with batched reads and optional resume by row. |
| **Entry Point / Surface** | Coding Engine CLI: `npx nest start --entryFile app.command -- archive-documents-based-on-sheet.command` with `--sheetId` (required), optional `--tab` (underscores for spaces, e.g. `Xero_No_Fye`), `--processAll` or omit `--tab` to process all tabs, `--startRow` (resume), `--batchSize` (1–1000, default 100). Documented in repo `README.md`; production/staging CronJobs run with `--sheetId` from env (e.g. `GOOGLE_SHEET_ID`). |
| **Short Description** | Reads MongoDB document ObjectIds from column **A** of a Google Sheet tab in batches (skipping row 1 as header by default), maps tab names to `DocumentSheetTab` values where predefined, then calls `DocumentService.archiveDocumentsFromSheet` to set `is_archived`, `script_action` (ARCHIVE + tab-derived reason), and batch audit logs via Sleek Auditor. Single-tab mode paginates with `--startRow`/`--batchSize` and tracks last processed row for recovery; all-tabs mode iterates every sheet tab with default pagination. |
| **Variants / Markets** | SG, HK (CronJobs and envs in repo suggest regional deployments; other markets Unknown) |
| **Dependencies / Related Flows** | Google Sheets API (`GoogleSheetsService`: read-only scope, rate limiting, retries); `GOOGLE_SHEETS_CREDENTIALS`; `DocumentService.archiveDocumentsFromSheet` → `processAuditLogsByBatch` → `SleekAuditorService.bulkInsertLogsToSleekAuditor`; tab mapping `TAB_MAPPINGS` / `DocumentSheetTab` |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `documentdetailevents` (MongoDB — `find` for existing/archive eligibility, `updateMany` to archive and set `script_action`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Confirm whether any environments rely on tabs outside `TAB_MAPPINGS` for audit messaging (fallback slugifies tab name); confirm whether column A is always exclusively document IDs in operational sheets. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Command (`src/commands/archive-documents-based-on-sheet/command/archive-documents-based-on-sheet.command.ts`)

- **`ArchiveDocumentsBasedOnSheetCommand`:** `@Command({ name: 'archive-documents-based-on-sheet.command', description: 'Archive documents based on Google Sheets data' })`.
- **`run()`:** Builds `IProcessingState`; resolves `tabsToProcess` via `shouldProcessAll = processAll || !tabName` → either `getSheetTabs(sheetId)` or `[tabName]`; loops `processAllTabs` → per tab `processSingleTab` (paginated `while (hasMore)`).
- **`processSingleTab`:** Calls `processDocumentsFromSheetWithPagination` then `processBatchForDocuments` when IDs exist; updates `lastProcessedRow` for single-tab resume.
- **`processBatch`:** `processBatchForDocuments(documentIds, mappedTabName)`; on failure records `IFailedBatchDetail` (rows, tab, error).
- **`getTabMapping`:** Uses `TAB_MAPPINGS` or lowercases + spaces to underscores for unmapped tabs.
- **Options:** `-s/--sheetId`, `-t/--tab` (underscores → spaces), `--processAll`, `--startRow`, `--batchSize`; exits `1` on top-level error, `0` on success.

### Service (`src/commands/archive-documents-based-on-sheet/services/archive-documents-based-on-sheet.service.ts`)

- **`processDocumentsFromSheetWithPagination`:** Delegates to `GoogleSheetsService.fetchSheetData(sheetId, tab, startRow, batchSize)`.
- **`processBatchForDocuments`:** `documentService.archiveDocumentsFromSheet({ tab: tabName as DocumentSheetTab, documentIds })`.
- **`getSheetTabs`:** `googleSheetsService.getSheetTabs(sheetId)`.

### Google Sheets (`src/common/services/google-sheets.service.ts`)

- **`fetchSheetData`:** Range `${tabName}!A${startRow}:A${endRow}`; first column values → `documentIds`; `DEFAULT_START_ROW` / `BATCH_SIZE` from archive enum; handles missing tab (empty batch), metadata, pagination `hasMore`.

### Document service (`src/document/document.service.ts`)

- **`archiveDocumentsFromSheet`:** Validates `tab` and `documentIds`; filters `Types.ObjectId.isValid`; loads existing docs; archives only those with `!is_archived` via `updateMany` with `$set`: `is_archived: true`, `script_action: { action: DocumentScriptActionEnum.ARCHIVE, action_reason: getTabNameForScriptAction(tab) }`; builds `BasicAuditLogDto[]` and `processAuditLogsByBatch` when modifications occurred.

### Enums (`src/commands/archive-documents-based-on-sheet/enum/archive-documents.enum.ts`)

- **`TAB_MAPPINGS`:** e.g. `'SB Filed Fye'`, `'Xero No Fye'` → `DocumentSheetTab` values; **`BATCH_SIZE`** `100`, **`DEFAULT_START_ROW`** `2` (header row 1).

### Operations

- Kubernetes CronJobs (e.g. `kubernetes/production-sg/Cronjob.yaml`, `production-hk`, staging/sit) invoke the same command with `--sheetId "$GOOGLE_SHEET_ID"`.
