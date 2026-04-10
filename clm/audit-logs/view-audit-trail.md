# View Audit Trail

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | View Audit Trail |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables operators to review a filterable history of platform actions scoped by company and tags, supporting compliance audits and operational oversight. |
| **Entry Point / Surface** | Internal Ops Tool or Admin Panel > Audit Logs (`GET /audit-logs`) |
| **Short Description** | Provides a queryable view of audit log entries filterable by company and tags. The billing backend proxies the request to the sleek-auditor external service, which is the authoritative store for all log records. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | sleek-auditor service (authoritative log store); audit entries are written by invoice, payment, subscription, credit card, coupon, external invoice, and company archiving flows across sleek-billings-backend |
| **Service / Repository** | sleek-billings-backend, sleek-auditor (external) |
| **DB - Collections** | None directly — delegated to sleek-auditor service |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | No auth guard (`@UseGuards`) on `AuditLogsController` — confirm whether this endpoint is protected by an app-level guard or API gateway. Unknown which frontend or internal tool consumes this endpoint. Markets not determinable from code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `audit-logs/audit-logs.controller.ts` — `GET /audit-logs`, query params via `AuditLogQueryDto`
  - No explicit `@UseGuards` decorator on controller or method

### Query surface
- `audit-logs/dtos/audit-log-query.dto.ts`
  - `tags: string[]` — filter by one or more tags
  - `companyId?: string` — scope results to a specific company (MongoDB ObjectId)

### Service logic
- `audit-logs/audit-logs.service.ts` — `getAuditLog()`
  - Forwards all query params to `SLEEK_AUDITOR_URL/audit-logs` via HTTP GET
  - Authenticates with `SLEEK_AUDITOR_API_KEY` and `SLEEK_AUDITOR_USER_AGENT` headers
  - Returns raw response data from auditor service

### Write path (context — not this feature's scope)
- `addAuditLog()` enriches entries with user details (via `UserService`) and company name (via `CompanyService`), then POSTs to `SLEEK_AUDITOR_URL/audit-logs` with exponential-backoff retry (max 3 retries, 1s base delay)
- Log entry structure: `entryType`, `text`, `action` (create/read/update/delete), `actionBy`, `company`, `oldValue`, `newValue`, `tags`
- Called from 9+ modules: invoice, payment, customer-subscription, archive-company, coupon, subscriptions-config, payment-method, external-invoice, credit-card

### Audit log action enum
- `audit-logs/consts/audit-log.const.ts`: `AuditLogAction { create, read, update, delete }`

### Module wiring
- `audit-logs/audit-logs.module.ts` — imports `HttpModule`, `CompanyServiceModule`; exports `AuditLogsService` for use by other modules
