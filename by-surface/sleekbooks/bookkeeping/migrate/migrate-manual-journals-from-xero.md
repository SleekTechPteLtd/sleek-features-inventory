# Migrate manual journals from Xero

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Migrate manual journals from Xero |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Manual journal entries and their attachments from a Xero tenant are reproduced in SleekBooks (ERPNext) so migrated books stay aligned with source adjustments and supporting files. |
| **Entry Point / Surface** | `xero-sleekbooks-service` HTTP API: `POST /migrate/:companyId/mj` to run migration, `GET /migrate/:companyId/mj` intended for status — both behind `SleekBackAuthGuard` (back-office / operator access). |
| **Short Description** | Loads the active migration record for context, lists manual journals from Xero, skips entries that are not `POSTED` or `PAID` (logged only), creates missing journal entries in SleekBooks via `createManualJournalFromXero` with Xero line detail, and for journals with attachments downloads files from Xero and uploads them to the matching ERP journal. Success and errors are logged to the app logger. The GET handler currently delegates to COA progress logic, and `getMJProgress` is a placeholder string. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** Xero Accounting API (`getManualJournals`, `getManualJournal`, attachment endpoints). **Downstream:** SleekBooks/ERPNext journal APIs (`checkManualJournal`, `createManualJournalFromXero`, `checkJournalFULL`, `uploadInvoiceFile`). **Adjacent:** Chart of accounts migration (accounts must exist for lines); bank migration may create related “Bank Entry” journals via the same helper. |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | `migrations` (read — `getLastestMigration` loads `Migration` by `_id` for company context); `apploggers` (write — structured migration logs via `AppLoggerService.createLog` for category `manualjournal`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `GET /:companyId/mj` calls `MigrateService.getCOAProgress` instead of `getMJProgress` — is that a copy-paste bug? `getMJProgress` returns a static message unrelated to MJ. Should non-`POSTED`/`PAID` journals be skipped permanently or retried later? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/migrate/migrate.controller.ts`

- **`POST /migrate/:companyId/mj`** — `startMJMigration`: `SleekBackAuthGuard`, `ValidationPipe`, passes `request.xero` into `MigrateService.createMJMigration`, responds `201` with `newCOAMigration` property name (payload is MJ run result).
- **`GET /migrate/:companyId/mj`** — `getMJMigration`: `SleekBackAuthGuard`, calls **`getCOAProgress(query)`** (not MJ-specific), responds `200` with `coaMigration` key — likely incorrect wiring for MJ status.
- `@ApiOperation` summaries: “Create MJ Migration”, “Get Status of Company MJ”.

### `src/migrate/migrate.service.ts`

- **`createMJMigration`**: `getLastestMigration` → `xeroService.getManualJournals(companyTenantId)` → per journal: optional skip when status not `POSTED`/`PAID`; `sleekBooksService.checkManualJournal(companyName, manualJournalID)`; if ERP empty, `getManualJournal` + `createManualJournalFromXero(mjDetail, journalLines, companyRegNo, 'Journal Entry', manualJournalID)`; if `hasAttachments`, `checkDownloadDirecXeroMJ` downloads via `getManualJournalAttachments` / `getManualJournalAttachmentByFileName`, then uploads to ERP with `uploadInvoiceFile` on `Journal Entry` when missing on the ERP doc; success log `appLoggerService.createLog(..., 'manualjournal', ...)` with `MJ_SUCCESS`.
- **`checkDownloadDirecXeroMJ`**: local filesystem under `__dirname/manualjournals/{tenantId}/{manualJournalID}/`, syncs attachments to ERP.
- **`getMJProgress`**: logs and returns static `'Fiscal year in progress'` — placeholder, not used by controller as written.

### `src/xero/xero.service.ts`

- **`getManualJournals`**, **`getManualJournal`**, **`getManualJournalAttachments`**, **`getManualJournalAttachmentByFileName`** — Xero `accountingApi` wrappers.

### `src/migration/schemas/migration.schema.ts`

- **`Migration`** model — company and migration pipeline fields; used as context for `getLastestMigration`.

### Auth

- **`SleekBackAuthGuard`** — operator/back-office access pattern consistent with other `migrate/*` routes.

**Usage confidence rationale:** Create path is substantial and integrated with Xero and SleekBooks; status GET is miswired and progress helpers are placeholders, so “monitor migration progress” is not fully supported in code as named.

**Criticality rationale:** Manual journals adjust ledger balances; errors or omissions affect financial accuracy during Xero-to-SleekBooks migration.
