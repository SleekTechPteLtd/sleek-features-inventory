# Align PBAC role templates with access control

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Align PBAC role templates with access control |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (Sleek Access Control or internal automation triggers refresh); callers must pass `userService.authMiddleware` |
| **Business Outcome** | Cached role templates in Redis stay consistent with the Sleek Access Control service so default role resolution (Director, Shareholder, Company Owner, etc.) and downstream PBAC behaviour match the source of truth. |
| **Entry Point / Surface** | Authenticated API `POST /sleek-access-control/web-hook/update-role-templates` — integration/webhook-style endpoint, not an end-user screen; intended for access-control or ops automation after template changes |
| **Short Description** | Fetches the current role template list from Sleek Access Control (`GET .../admin/role-template-api`) and stores the response in Redis under `pbac-role-templates-key`. `getHighestRoleHierarchy` reads this cache when mapping company users to default PBAC roles; if the cache is empty it populates via the same fetch. Application data load can also warm the cache at startup. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Sleek Access Control HTTP API (`/admin/role-template-api`); Redis via `redisUtil.setRedisCache` / `getRedisCache`; `getHighestRoleHierarchy` → `setDefaultPolicy` / company-user PBAC flows; `data-loader-service.loadPBACRolesTemplates` (startup warm) |
| **Service / Repository** | sleek-back |
| **DB - Collections** | None for this path — Redis cache only (MongoDB touched elsewhere in `pbac-policy-service.js` for other PBAC features) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `controllers/sleek-access-control.js` calls `sleekAccessControl.setRoleTemplatesCache()` from `sleek-access-control-service.js`, but that module does not define or export `setRoleTemplatesCache` — the implementation is `PBACService.setRoleTemplatesCache` in `services/pbac-policy-service.js`. Confirm whether the webhook route is broken at runtime or wired elsewhere. Who is authorized to call the webhook (any authenticated user vs service account) is not explicit beyond `authMiddleware`. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Route:** `POST /sleek-access-control/web-hook/update-role-templates` — `userService.authMiddleware` — success/error via `successResponseHandler` / `errorResponseHandler` — `controllers/sleek-access-control.js` (handler invokes `sleekAccessControl.setRoleTemplatesCache()` per current file).
- **Implementation:** `setRoleTemplatesCache` — `PBACHelper.getResource` to `${config.sleekAccessControl.baseUrl}/admin/role-template-api`; on success with `response.data`, `redisUtil.setRedisCache("pbac-role-templates-key", response)` when `NODE_ENV !== 'test'`; errors logged and `logErrorPBACAlert` — `services/pbac-policy-service.js`.
- **Consumers:** `getHighestRoleHierarchy` loads `redisUtil.getRedisCache("pbac-role-templates-key")` and falls back to `setRoleTemplatesCache()` if missing; maps `CompanyOwnerRole`, `DirectorRole`, `CorporateShareholderRole`, `ShareholderRole`, `StandardUser` from `roleTemplates.data` — same file.
- **Startup warm:** `loadPBACRolesTemplates` → `pbacService.setRoleTemplatesCache()` — `services/data-loader-service.js`.
