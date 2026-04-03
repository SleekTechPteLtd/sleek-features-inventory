# Clear migrations stuck in review or ready

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Clear migrations stuck in review or ready |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Stale bookkeeping migration documents left in `review` or `ready` are removed from the database so operator views and downstream automation are not blocked by abandoned or inconsistent queue rows. |
| **Entry Point / Surface** | `xero-sleekbooks-service` **CLI** — Nest `nestjs-command` handler **`script:deleteMigrationInReviewOrReady`** (invoked when the app is started in command mode with that command name). Not exposed as an HTTP route. |
| **Short Description** | Operators run a maintenance command that streams all migration documents whose `status` is `review` or `ready`, deletes each by `_id`, and logs how many succeeded versus failed. |
| **Variants / Markets** | `SG`, `HK`, `AU`, `UK` (migration `region` enum in schema; command runs against the connected MongoDB for the deployed platform instance). |
| **Dependencies / Related Flows** | **Same repo**: `MigrationService.deleteMigrationInReviewOrReady`; `Migration` Mongoose model. **Related**: `migrate:eligible-companies` / `autoMigrateEligibleCompaniesFromSleekback` can promote existing `review`/`ready` rows to `posted` instead of deleting — this script is the destructive cleanup path when stale state must be removed entirely. |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | `migrations` (Mongoose model `Migration`; deletes documents matching `{ status: { $in: ['review', 'ready'] } }`). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/app.command.ts`

- **`@Command({ command: 'script:deleteMigrationInReviewOrReady', describe: 'script to delete migration in review or ready' })`** — `deleteMigrationInReviewOrReady()` sets `GlobalService.isStartFromCommand = true`, logs start/end, awaits `migrationService.deleteMigrationInReviewOrReady()`, then `process.exit(0)` on success or `process.exit(1)` on error.

### `src/migration/migration.service.ts`

- **`deleteMigrationInReviewOrReady()`** — `find({ status: { $in: ['review', 'ready'] } }).cursor()`, iterates with `while (migration)`, for each document calls `deleteOne({ _id: migration._id })`, increments success/fail counters, uses `LoggerService` with `feature` context from `migration.companyId`, logs per-document start/end and a final summary: `Results: number of deleted: ${counterSuccess} - number of failed: ${counterFail}`.

### `src/migration/schemas/migration.schema.ts`

- **`status`** — enum includes `review`, `ready`, `posted`, `inprogress`, `completed`, `failed`, `aborted`, `deleted`; default `'review'`. Confirms the maintenance filter matches first-class workflow states before a migration is posted or in progress.
