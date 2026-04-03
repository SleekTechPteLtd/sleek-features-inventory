# Sign out of coding engine session

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sign out of coding engine session |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Authenticated user (Finance User, Bookkeeper, or Operations User using the coding engine) |
| **Business Outcome** | Users can end their session with the accounting coding engine so cached identity tied to their bearer token is cleared, reducing stale-session risk on shared devices and after access changes. |
| **Entry Point / Surface** | API: `POST /api/logout` on acct-coding-engine (client must send `Authorization` header); exact in-app navigation to this call is product-dependent |
| **Short Description** | After authentication via `AuthGuard`, the service deletes the Redis-backed auth cache entry keyed by the request’s `Authorization` header, clearing the cached SleekBack user profile for that token. Returns a simple confirmation string. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **AuthGuard** (same token used for all guarded routes); **SleekBack** (`SleekBackService`) for user resolution when cache miss; **Redis** via Nest `cache-manager` (`AuthCacheService`). Upstream: clients obtain tokens from Sleek identity flows. Downstream: subsequent requests with the same token miss cache and re-resolve user via SleekBack until cached again. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | None — session state is Redis cache keys only (no MongoDB writes or reads in this flow) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether product UIs consistently call this endpoint on “sign out” vs only token discard; whether `console.log` of the authorization header in `logout` is intentional for production. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/app.controller.ts`

- **`POST /api/logout`**: `@UseGuards(AuthGuard)` — only callers presenting a resolvable `Authorization` header reach the handler.
- Handler calls `authCacheService.invalidateCache(request.headers['authorization'])`, removing the cache entry for that token (typed as `CacheService` from `@app/cache/cache.service`, injected as `AuthCacheService`).
- Returns literal `'logged out'`.

### `src/common/auth/auth.guard.ts`

- Reads `request.headers['authorization']`; rejects with `UnauthorizedException` if missing.
- Uses `authCacheService.getCache` / `setCache` / `reinvalidateCache` on other routes; establishes `request.user` from cache or `sleekBackService.getUserInfoFromSleekBackByAuthorizationToken`. Logout reuses the same token keying model as the guard.

### `src/cache/auth-cache/auth-cache.service.ts`

- Implements `CacheService`; `invalidateCache(key)` → `cacheManager.del(key)` against the configured store (Redis per Nest cache setup).
- `setCache` / `getCache` use TTL from `REDIS_CACHE_TTL_IN_MS` (default 5 minutes).
