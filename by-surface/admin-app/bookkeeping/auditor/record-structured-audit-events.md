# Record structured audit events

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Record structured audit events |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User, Operations User, System (via integrated clients such as banking flows) |
| **Business Outcome** | Client applications can persist company- and user-scoped audit records (actions and before/after values) so compliance and accounting retain a durable, queryable event history. |
| **Entry Point / Surface** | Authenticated HTTP API on sleek-back: `PUT /api/log/company`, `PUT /api/log/user` (requires signed-in user via `userService.authMiddleware`). |
| **Short Description** | Handlers normalize request bodies into structured audit payloads (actor, scoped entity, comment text, action type, optional old/new values) and forward them to the external Sleek Auditor service. Writes are skipped when `NODE_ENV` is `test`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **External:** Sleek Auditor HTTP API (`config.sleekAuditor.sleekAuditorBaseUrl`, `PUT /api/log`, authorized via `request-helper-sleek-auditor` headers). **Related:** Company comments and comment listing on `GET`/`PUT` …`/api/log/company/:companyId/comment` (same handler module, comment `entry_type`); internal `saveAuditLog` helper used for programmatic writes. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | None in these files; persistence is delegated to Sleek Auditor. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Confirm which client apps and markets call these routes in production; confirm retention and PII handling policies on the Sleek Auditor side. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Router (`controllers-v2/auditor.js`):** Registers `PUT /api/log/company` → `saveCompanyAuditLog`, `PUT /api/log/user` → `saveUserAuditLog` with `userService.authMiddleware`; comment routes `GET`/`PUT` …`/api/log/company/:companyId/comment`.
- **Handlers (`controllers-v2/handlers/auditor/all.js`):** `saveCompanyAuditLog` reads `company`, `user`, `comment`, `actionType`, `oldValue`, `newValue` from `req.body`, builds payload via `buildAuditLog`, calls `saveAuditLog` (skipped in `test`). `saveUserAuditLog` reads `user`, `actionByUser`, `comment`, `actionType`, `oldValue`, `newValue`, builds via `buildUserAuditLog`. `saveAuditLog` issues `PUT` to `${sleekAuditorBaseUrl}/api/log` with `putResource`.
- **Payload builders (`utils/auditor-utils.js`):** `buildAuditLog` sets `entry_type` (default `"log"`), `actionBy` (user fields), `company` (id, name, uen), `text`, `action`, `old_value`, `new_value`. `buildUserAuditLog` sets `entry_type: "log"`, `actionBy` (actor), `user` (subject user), same text/action/value fields.
- **HTTP client (`controllers-v2/utlities/request-helper-sleek-auditor.js`):** `putResource` sends authorized requests to Sleek Auditor (not shown in feature file list; used by handlers).
