# Review platform audit logs

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Review platform audit logs |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (users in the `Sleek Admin` group; authenticated via `userService.authMiddleware`) |
| **Business Outcome** | Compliance and operations teams can inspect who did what, when, and in which company context across the platform, with search and pagination, to support audits and day-to-day oversight. |
| **Entry Point / Surface** | Sleek Admin (or any client using admin credentials) — HTTP API on sleek-back: `GET /v2/sleek-auditor-v2/audit-logs` with optional query filters (see Evidence). Exact admin UI navigation labels are not defined in the referenced files. |
| **Short Description** | Authenticated Sleek Admin users retrieve paginated audit activity from the central Sleek Auditor service. Filters include company, actor, action type, free text, request id, tags, and date range; results support sort and page metadata from the upstream API. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Auth**: `userService.authMiddleware` (JWT / token resolution). **Access**: `accessControlService.isIn("Sleek Admin")` — membership in the Sleek Admin group. **Upstream**: `getAuditLog` calls the configured Sleek Auditor HTTP API (`config.sleekAuditorNode.baseUrl`) with `SLEEK_AUDITOR_API_KEY` (see `http-request-utils`). **Related**: `saveAuditLog` / `addAuditLogSuccess` in the same module write audit entries to that service from other flows; legacy `controllers-v2/auditor.js` under `/v2/sleek-auditor` is a separate surface. |
| **Service / Repository** | sleek-back (proxy); Sleek Auditor service (external HTTP API, base URL from config) |
| **DB - Collections** | None in sleek-back for this read path — audit records are served by the external Sleek Auditor API. Storage schema and database for that service are not evidenced in these files. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/auditor-v2.js`

- **Mount** — Registered in `app-router.js` at `/v2/sleek-auditor-v2` (see `app-router.js`), so the audit log list route is `GET /v2/sleek-auditor-v2/audit-logs`.

- **`validateGetQueryMiddleware`** — Joi-validated query: `page`, `pageSize`, `orderBy` (default `createdAt`), `sortOrder` (default `desc`), `companyId`, `companyName`, `actionBy`, `actionByEmail`, `type`, `text`, `requestId`, `tags` (array), `startDate`, `endDate`. Invalid requests return tenant `GENERIC.INVALID_REQUEST`.

- **`GET /audit-logs`** — Middleware chain: `validateGetQueryMiddleware` → `userService.authMiddleware` → `accessControlService.isIn("Sleek Admin")`. Handler calls `getAuditLog({ queryString: req._parsedUrl.query })` and responds with JSON `{ data: auditLogRes.records, ...(auditLogRes._metaData || {}) }`. Errors map to `GENERIC.INTERNAL_SERVER_ERROR`.

### `modules/sleek-auditor-node/services/auditor-node-service.js`

- **`getAuditLog({ queryString })`** — In non-`test` environments, `GET` `${config.sleekAuditorNode.baseUrl}/audit-logs?` + query string via `getResource` from `utilities/http-request-utils`. Returns parsed response body (expected to include `records` and optional `_metaData` used by the controller). Throws on failure (logged).

- **`saveAuditLog` / `addAuditLogSuccess`** — Illustrates the write side to the same base URL (`POST /audit-logs`); not required for the read capability but shows the external service boundary.

### `modules/sleek-auditor-node/utilities/http-request-utils.js`

- **`getResource`** — Axios GET with `Authorization: process.env.SLEEK_AUDITOR_API_KEY` and headers from `getDefaultHeaders`; errors wrapped as `[getResource] Error from Sleek Auditor API: ...`.

### `services/access-control-service.js`

- **`isIn(groupName)`** — After `req.user` is set, requires `AccessControlService.isMember(req.user, groupName)`; otherwise `401`.
