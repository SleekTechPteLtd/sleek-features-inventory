# Reset Application Cache

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Reset Application Cache |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (internal operator with bearer token) |
| **Business Outcome** | Operators can force a full cache invalidation so that fresh CMS content and application data (e.g. Xero tax rates, service configuration) is served immediately after configuration or content changes, without waiting for TTL expiry. |
| **Entry Point / Surface** | Internal API — `POST /api/cache-manager/reset` (no UI surface; called directly by operators or tooling) |
| **Short Description** | Invalidates both the Sleek CMS in-process cache and the Redis-backed NestJS application cache in one atomic operation. Returns `{ ok: true }` on success. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Sleek CMS (`@sleek-sdk/sleek-cms` `CmsCacheManager`); Redis cache store (`cache-manager-redis-yet`); downstream: Xero tax rates cache, subscription service config cache |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | None (Redis only — key prefix: `${PLATFORM}-sleek-billings-backend-`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | 1. `@TODO: check admin role` comment in controller — no role restriction is currently enforced; any authenticated bearer token can trigger a full cache flush. Should a specific admin/operator role be required? 2. `reset()` on the Redis store flushes **all** keys for this service's prefix — could impact concurrent users if called during peak hours. Scope intentional? 3. Markets unknown — no market-specific cache key logic observed. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Controller**: `src/cache-manager/cache-manager.controller.ts`
  - `POST /api/cache-manager/reset` — protected by `@Auth()` (bearer token, `AuthGuard` + `PermissionsGuard`; no permission set, so any authenticated user qualifies — see TODO comment)
  - Calls `CmsCacheManager.resetCache()` from `@sleek-sdk/sleek-cms` (in-process CMS cache)
  - Calls `this.cacheManager.reset()` (flushes entire Redis namespace for this service)

- **Module**: `src/cache-manager/cache-manager.module.ts`
  - Global NestJS module; Redis store configured via `cache-manager-redis-yet`
  - Key prefix: `` `${process.env.PLATFORM}-sleek-billings-backend-` ``
  - On startup (`onModuleInit`) sets `cache-manager-config` key with 1-hour TTL as a health check

- **Known cached data (reset scope)**:
  - `xero_tax_rates_${clientType}` — Xero tax rates, cached 24 hours (`src/xero/services/xero.service.ts`)
  - `cache-manager-config` — service startup diagnostic value, 1-hour TTL
  - CMS content/configuration data managed by `@sleek-sdk/sleek-cms`

- **Auth**: `src/shared/auth/auth.decorator.ts` — `@Auth()` applies `AuthGuard` (bearer token) and `PermissionsGuard`; no specific permission or group guard applied to this endpoint
