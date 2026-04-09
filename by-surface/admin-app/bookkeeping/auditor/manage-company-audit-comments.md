# Manage company audit comments

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage company audit comments |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User, Operations User, Bookkeeper (authenticated Sleek platform users) |
| **Business Outcome** | Teams can read paginated company comment history and add comments so the shared audit narrative stays in one central auditor service. |
| **Entry Point / Surface** | Sleek API: `GET` / `PUT` `/v2/sleek-auditor/api/log/company/:companyId/comment` (query `skip`, `limit` on GET; default limit 20, skip 0). |
| **Short Description** | Authenticated users list comment-type audit entries for a company with skip/limit paging, and submit new comment payloads; sleek-back forwards both operations to the central Sleek Auditor HTTP API using service credentials. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **External:** Sleek Auditor (`config.sleekAuditor.sleekAuditorBaseUrl`) — `GET` `/api/log` with `company_id`, `entry_type=comment`, `skip`, `limit`; `PUT` `/api/log` with request body. Auth to auditor: `Authorization` from `config/sleekAuditor/credentialsFile` via `request-helper-sleek-auditor`. **Same router:** `PUT` `/v2/sleek-auditor/api/log/company` and `/api/log/user` write structured company/user audit logs (e.g. sleek-bank integration), built with `auditor-utils` — related audit trail but not the comment list/post pair. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | None in sleek-back for this flow; comment storage is delegated to the Sleek Auditor service. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | On GET/PUT comment handlers, `catch` blocks log errors but do not always send an explicit HTTP error response — confirm client-visible behaviour. Confirm market-specific retention or visibility rules for comments (not visible in this code). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Router mount:** `app-router.js` — `router.use("/v2/sleek-auditor", require("./controllers-v2/auditor"))`.
- **Routes & auth:** `controllers-v2/auditor.js` — `GET` `/api/log/company/:companyId/comment` → `userService.authMiddleware`, `getCompanyComments`; `PUT` same path → `saveCompanyComment`. `PUT` `/api/log/company` → `saveCompanyAuditLog`; `PUT` `/api/log/user` → `saveUserAuditLog`.
- **Comment read:** `getCompanyComments` — reads `limit` (default 20), `skip` (default 0); calls `getResource` with Sleek Auditor URL `…/api/log?company_id=${companyId}&entry_type=comment&skip=${skip}&limit=${limit}` (`controllers-v2/handlers/auditor/all.js`).
- **Comment write:** `saveCompanyComment` — `putResource` to `${sleekAuditorBaseUrl}/api/log` with `data: req.body` (same file).
- **HTTP client:** `controllers-v2/utlities/request-helper-sleek-auditor.js` — `getResource` / `putResource` (axios GET/PUT, shared `Authorization` header).
- **Related helpers:** `getCompanyCommentDirectly(companyId)` — internal GET without paging params (same `entry_type=comment`); `getAuditLogs` duplicates comment query shape (not wired in `auditor.js` exports for routes examined). `buildAuditLog` / `buildUserAuditLog` in `utils/auditor-utils.js` support structured `PUT` `/api/log/company` and `/api/log/user`, not the comment CRUD pair.
