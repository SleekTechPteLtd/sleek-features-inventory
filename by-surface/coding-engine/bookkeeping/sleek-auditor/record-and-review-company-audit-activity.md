# Record and review company audit activity

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Record and review company audit activity |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, Finance User, System |
| **Business Outcome** | Operators and integrated systems can append audit events and review paginated history by company and tags so accounting-related activity remains traceable for compliance. |
| **Entry Point / Surface** | Supplier Rules Service REST API under `sleek-auditor` (`GET` / `POST` `…/sleek-auditor/logs`); audit lines are also written from other modules in this service (supplier, supplier-rules, smart-rules, customer) via `SleekAuditorService.insertLogsToSleekAuditor`. |
| **Short Description** | This module is an HTTP client to the external Sleek Auditor service: it posts structured audit payloads (actor, company, tags, action, message, step, codes) and fetches paginated audit logs filtered by `companyId`, `page`, `pageSize`, and `tags`, with results normalized into DTOs including actor and company fields. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **External:** Sleek Auditor HTTP API (`SLEEK_AUDITOR_BASE_URL`, `GET`/`POST` `/audit-logs`, `Authorization` via `SLEEK_AUDITOR_API_KEY`). **Internal callers (write path):** `SupplierService`, `SupplierRuleService`, `SmartRuleService`, `CustomerService` inject `SleekAuditorService` to emit logs. |
| **Service / Repository** | supplier-rules-service |
| **DB - Collections** | None used by this module at runtime; audit storage is delegated to Sleek Auditor. A Mongoose schema file `schemas/sleek-auditor.schema.ts` exists in-repo but is not registered on `SleekAuditorModule` and is not referenced elsewhere. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `SleekAuditorController` declares no Nest guards in the examined file—confirm whether global middleware or gateway auth applies. Confirm market-specific requirements for audit retention (variants unknown from code). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Routes:** `SleekAuditorController` — `@Controller('sleek-auditor')`; `GET logs` → `getLogs` → `SleekAuditorService.getLogsFromSleekAuditor`; `POST logs` → `insertLogs` → `insertLogsToSleekAuditor` (`sleek-auditor.controller.ts`).
- **Swagger:** `@ApiOperation` summaries “Get Logs from Sleek Auditor” / “Insert Logs to Sleek Auditor”; query params `companyId`, `pageSize`, `page`, `tags` (all required per decorators); body type `SleekAuditorDto` for insert.
- **External HTTP:** `getLogsFromSleekAuditor` — `HttpService.get` to `${SLEEK_AUDITOR_BASE_URL}/audit-logs` with params `companyId`, `pageSize`, `page`, `tags`, `sortOrder: 'desc'`; maps response `records` to `SleekAuditorDto` (company id, entry type, message, code, actor names/email, category as `event`, UEN, action, step, timestamps). `insertLogsToSleekAuditor` — `HttpService.post` to same base `/audit-logs` with payload `actionBy`, `company`, `text` (from `event`), `action`, `newValue`, `entryType`, `tags` (`sleek-auditor.service.ts`).
- **DTOs / response:** `SleekAuditorDto`, `SleekAuditorResponseDto` (`data`, `_metaData`) (`dtos/sleek-auditor.dto.ts`).
- **Module wiring:** `SleekAuditorModule` imports `HttpModule` only; no `MongooseModule.forFeature` (`sleek-auditor.module.ts`).
- **Downstream usage of write API:** `insertLogsToSleekAuditor` called from `supplier.service.ts`, `supplier-rules.service.ts`, `smart-rules.service.ts`, `customer.service.ts` (grep / imports).
