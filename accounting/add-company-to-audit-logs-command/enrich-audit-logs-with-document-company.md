# Enrich audit logs with document company

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Enrich audit logs with document company |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (scheduled or manually triggered batch job; operators run the Nest CLI command when needed) |
| **Business Outcome** | Audit log rows in the central logs store carry the correct company id and name for the related coding-engine document so activity remains traceable to the right entity for compliance and investigations. |
| **Entry Point / Surface** | **acct-coding-engine** CLI: `npx nest start --entryFile app.command -- add-company-to-audit-logs.command` (optional `--dryRun`, `--batchSize <n>`). Kubernetes **CronJob** definitions exist per environment (SG/HK, staging/SIT/production); jobs are **suspended** with a placeholder schedule in production manifests, so runs are typically **manual** until explicitly enabled. |
| **Short Description** | Streams all documents from the receipts database (`company`, `company_name`), builds a map keyed by document id, finds audit log documents whose `tags` include `CES_<documentId>`, and bulk-updates each log’s embedded `company` (`_id`, `name`) when they differ from the document. Uses batched cursors, chunked `$in` queries on tags, optional dry-run, and a separate MongoDB client to the logs database (`DB_SLEEK_LOGS`). |
| **Variants / Markets** | SG, HK (CronJob manifests and README reference multi-region deployment; other markets not evidenced in-repo) |
| **Dependencies / Related Flows** | **Documents** in `documentdetailevents` (source of truth for company fields). **Audit / activity logs** in `sleek_logs` keyed by `CES_`-prefixed tags (aligns with coding-engine document correlation). Config: `DB_HOST`, `DB_SECRET`, `DB_SLEEK_LOGS`. Related: broader **audit trail** and any emitters that write logs with `CES_<id>` tags. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | **Read:** `documentdetailevents` (Mongoose `Document` on connection `sleek_receipts`). **Read/write:** `sleek_logs` (native driver collection name `DBConnectionName.SLEEK_LOGS` on database `DB_SLEEK_LOGS`). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether a steady cron schedule will replace manual triggers after `suspend` is lifted; exact operational runbook and frequency. Whether logs without `CES_` tags or with mismatched tag formats are out of scope by design. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/commands/add-company-to-audit-logs/add-company-to-audit-logs.command.ts`

- **Nest Commander** `@Command({ name: 'add-company-to-audit-logs.command' })`; description frames it as a cron-style job to add company data from documents to audit logs.
- **Options:** `--dryRun` (parse returns `true` when flag present — no DB writes in service), `--batchSize <size>` validated between `DEFAULT_BATCH_SIZE` (1000) and `MAX_BATCH_SIZE` (10000) from enum.
- **Run:** logs options, calls `AddCompanyToAuditLogsService.execute`, `process.exit(0|1)` on success/failure.

### `src/commands/add-company-to-audit-logs/add-company-to-audit-logs.service.ts`

- **Documents:** `documentModel.find({}, { _id: 1, company: 1, company_name: 1 }).cursor()` with `batchSize`, yields batches via `getDocumentsBatch()`.
- **Map:** `createDocumentCompanyMap` → `Map<documentId, { _id: company ObjectId, name: company_name }>`.
- **Logs connection:** separate `MongoClient` to URI built from `DB_HOST` / `DB_SECRET` / `DB_SLEEK_LOGS`; `logsCollection = db.collection('sleek_logs')` (enum value).
- **Matching:** for each batch, builds `tags` = `documentIds.map(id => 'CES_' + id)`; queries logs with `tags: { $in: tagChunk }`; paginates with `_id: { $gt: lastId }` and `limit(batchSize)`; 100ms delay between full pages to reduce load.
- **Skip if:** no `CES_` tag, no company in map, or `log.company` already matches document company id and name.
- **Updates:** `bulkWrite` with `updateOne` + `$set: { company: { _id, name } }`, `ordered: false`; dry-run logs sample only.
- **Stats:** documents processed, logs found/updated/skipped, errors per batch, timing summary.

### `src/commands/add-company-to-audit-logs/add-company-to-audit-logs.module.ts`

- Registers `Document` schema on `DBConnectionName.SLEEK_RECEIPTS` only; service handles logs DB outside Mongoose.

### `src/document/models/document.schema.ts`

- `@Schema({ collection: 'documentdetailevents', ... })` — confirms receipts-side collection name for streamed documents.

### `src/common/enum/db.enum.ts`

- `SLEEK_RECEIPTS = 'sleek_receipts'`, `SLEEK_LOGS = 'sleek_logs'` — collection identifier used for the logs collection.

### `kubernetes/*/Cronjob.yaml` (e.g. `production-sg`, `production-hk`)

- CronJob `add-company-to-audit-logs` runs the same CLI with Kafka producers/consumers disabled; **suspend: true** and placeholder schedule in sampled production manifest — indicates on-demand or future-scheduled operation.

### `README.md`

- Documents example invocations with `--dryRun` and `--batchSize` for local/ops use.
