# Legacy monolith health probe and request guard

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Legacy API liveness and coarse request throttling |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operators, load balancers, SRE |
| **Business Outcome** | Know the customer API is up; reduce accidental overload (abuse or bugs) on the shared monolith |
| **Entry Point / Surface** | `GET /api/health`; Express rate-limit middleware mounted before `appRouter` |
| **Short Description** | Health returns build version and fails fast if CORS whitelist is not initialised. A rate limiter keys primarily off `Authorization` (legacy token) or client IP and logs context when the cap is hit. |
| **Variants / Markets** | Per environment (`BUILD_VERSION`, config) |
| **Dependencies / Related Flows** | CORS / CMS notification whitelist bootstrap; distinct from Sleek Auth `/stats` / health ([platform-stats-and-health.md](./platform-stats-and-health.md)) |
| **Service / Repository** | `sleek-back` `app.js` |
| **DB - Collections** | `User` (lookup on limit breach for logging only) |
| **Evidence Source** | Codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Must Keep (until monolith is retired or replaced) |
| **Open Questions** | Whether health semantics should decouple from CORS whitelist; limiter window/max tuning |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-back

- `app.js` — `GET /api/health` (checks `cmsEventNotificationService.whitelists`, returns `BUILD_VERSION`).
- `app.js` — `express-rate-limit` (`limiter`): `windowMs`, `max`, `keyGenerator` using `req.headers.authorization || req.ip`, `onLimitReached` logging via `User.findOne({ auth_token: ... })`.

### customer-mfe

- N/A (health is server-side; browser calls API through configured `VUE_APP_PLATFORM_API` / proxies).

## Related

- [../scans-pending/sleek-back/README.md](../scans-pending/sleek-back/README.md)
