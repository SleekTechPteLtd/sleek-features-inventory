# Manage Sleek Auditor audit trail

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage Sleek Auditor audit trail |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, Bookkeeper, Finance User, System (integrated services posting audit events) |
| **Business Outcome** | Operators and integrated callers can review company-scoped audit history and record events in a central service so bookkeeping and related actions remain traceable for compliance. |
| **Entry Point / Surface** | API surface `sleek-auditor` on acct-coding-engine (`GET` / `POST` `sleek-auditor/logs`); product UI path not defined in this module (callers may be other Sleek apps or internal services). |
| **Short Description** | Proxies paginated audit log reads (by company, page, page size, tags, descending sort) and single-record inserts to the external Sleek Auditor HTTP API; maps remote payloads to `SleekAuditorDto` for responses. Other domain services call `SleekAuditorService` directly to append audit lines without using this controller. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Sleek Auditor** (`SLEEK_AUDITOR_BASE_URL`, `SLEEK_AUDITOR_API_KEY`) — `GET`/`POST` `/audit-logs`, bulk `POST` `/audit-logs/bulk`. Internal emitters include **reconciliation**, **document**, **feedback**, **ledger-transaction**, **sleek-digest**, **reconciliation-manual** scripts, and **generic** audit helpers. |
| **Service / Repository** | acct-coding-engine (proxy + integration); Sleek Auditor (remote persistence) |
| **DB - Collections** | None in acct-coding-engine for this capability — audit rows live in Sleek Auditor. A Mongoose schema file `schemas/sleek-auditor.schema.ts` exists but is not registered on `SleekAuditorModule`, so it does not drive local MongoDB usage here. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | No `@UseGuards` on `SleekAuditorController`; confirm whether global/auth or network policy protects these routes. Exact expected format for `tags` query string when forwarded to Sleek Auditor. Whether product-specific navigation labels exist for any UI that consumes this API. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/sleek-auditor/sleek-auditor.controller.ts`

- **Routes**: `GET sleek-auditor/logs` → `getLogs` → `getLogsFromSleekAuditor(companyId, pageSize, page, tags)`; `POST sleek-auditor/logs` → `insertLogs` → `insertLogsToSleekAuditor(loggerData)`. No route-level auth decorators on this controller.
- **Swagger**: `@ApiOperation` summaries “Get Logs from Sleek Auditor” / “Insert Logs to Sleek Auditor”; required query params `companyId`, `pageSize`, `page`, `tags` for GET; `POST` body type `SleekAuditorDto`; responses via `successResponseHandler` / `errorResponseHandler` with `SUCCESS_CODES.SLEEK_AUDITOR.*`.

### `src/sleek-auditor/sleek-auditor.service.ts`

- **Read path**: `HttpService.get` → `${SLEEK_AUDITOR_BASE_URL}/audit-logs` with params `companyId`, `pageSize`, `page`, `tags`, `sortOrder: 'desc'`, headers `Authorization: SLEEK_AUDITOR_API_KEY`, `Content-Type: application/json`. Maps `data.records` into `SleekAuditorDto` (company, entry type, message/code from `newValue`, actor names/email, category as `event`, `action`, `step`, `createdAt`, formatted `date`).
- **Write path**: `insertLogsToSleekAuditor` → `HttpService.post` → `${SLEEK_AUDITOR_BASE_URL}/audit-logs` with body `actionBy`, `company`, `text` (event), `action`, `newValue` (message, step, code), `entryType`, `tags`.
- **Additional methods** (not exposed on this controller): `insertMultipleLogsToSleekAuditor`, `bulkInsertLogsToSleekAuditor` → `POST` `/audit-logs/bulk` with `{ auditLogs }`.

### `src/sleek-auditor/dtos/sleek-auditor.dto.ts`

- **SleekAuditorDto**: `type`, optional `message`/`code`, `userFirstName`, `userLastName`, `userId`, `event`, `companyUen`, `action`, `step`, `companyId`, optional `createdAt`, optional `isAutoMigrate`.
- **SleekAuditorResponseDto**: `data: SleekAuditorDto[]`, `_metaData`.

### `src/sleek-auditor/interface/sleek-auditor.interface.ts`

- **InsertLogsToSleekAuditorDto**: `companyId` required; optional actor/company fields, `event`, `action`, `message`, `step`, `code`, `type`, `tags: string[]`.
- **BasicAuditLogDto**: used for bulk payloads (includes `tags`).

### `src/sleek-auditor/schemas/sleek-auditor.schema.ts`

- Mongoose class `SleekAuditor` with enums for `type`, `action`, `step` — **not** wired via `MongooseModule` in `sleek-auditor.module.ts`; evidence-only for intended field shapes.

### `src/sleek-auditor/sleek-auditor.module.ts`

- Registers `HttpModule`, `SleekAuditorService`, `SleekAuditorController` only — no local audit collection registration.
