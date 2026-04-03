# Authenticate and manage user sessions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Authenticate and manage user sessions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User, Operations User (end-user sign-in); System (M2M and internal tokens where applicable) |
| **Business Outcome** | Customers and staff can sign in, keep a stable session across visits, load their account context in the app, and end the session so tokens no longer authorize API access. |
| **Entry Point / Surface** | Sleek web and mobile clients calling the public user API (`POST /users/login`, `POST /users/login-keep`, `GET /users/me`, `POST /users/logout`); exact product navigation not defined in code. |
| **Short Description** | Password-based login issues or reuses a MongoDB-stored `auth_token` on the user record; “login-keep” supports persistent sessions with partner/tenant and 2FA gating. `GET /users/me` requires `Authorization` and enriches the profile via access, company, and optional file data. Logout clears the server-side token, invalidates Redis user cache, and returns a success message. `authMiddleware` also supports Auth0 JWT, admin SSO JWT, and the sleek-auth module for token resolution. |
| **Variants / Markets** | SG, HK, AU, UK (multi-region coding-engine merge via `getOtherRegionUserInfoForCE`); partner white-label MS flows differ by `client_type` and origin |
| **Dependencies / Related Flows** | Auth0 (`auth0-service.validateJWT`), Sleek Auth module (`AuthTokenService.getUserQueryByAuthToken`), Redis (`user:{userId}` cache), `get-user-access`, `get-user-company`, `get-user-partner-details`, partner service for domain/tenant; CDD suspension check for customer origins on non-`/users/me` paths; separate feature for `POST /users/login-with-sut` (admin single-use token exchange) |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `users` (persisted `auth_token`, password hash); Redis cache keys `user:{userId}` (not a Mongo collection) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether OpenAPI tag `v1` groups exactly these routes versus additional user routes in the same controller; alignment of 72-hour token refresh logic (`checkForExpiredUserAuthToken`) with client-facing session lifetime expectations. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Session establishment (password)

- `controllers/user-controller.js`: `POST /users/login` — `userService.login(email, password, { client_type })` → `{ auth_token }`.
- `controllers/user-controller.js`: `POST /users/login-keep` — `userService.loginKeep(email, password, origin, { client_type, country_code, domain_url })`; optional 2FA branch returns `{ user }` instead of `{ auth_token }` when tenant 2FA and user flag enable it and app features allow.
- `services/user-service.js`: `login` — `User.findOne` by email + `client_type`, `bcrypt.compare`, creates `auth_token` via `generateToken()` if absent, saves user.
- `services/user-service.js`: `loginKeep` — same plus partner/tenant checks for MS clients, Sleek Sign domain checks; reuses existing `auth_token` when present.

### Current user profile (authenticated)

- `controllers/user-controller.js`: `GET /users/me` — `userService.authMiddleware`; parallel `getUserAccess`, optional partner details, `File.populate`, `getUserCompany`; sets `isSuperAdmin`, role flags, `companies`, `last_accessed_company_id`; optional multi-region `userService.getOtherRegionUserInfoForCE`; returns `userService.sanitizeUserData(req.user)`.
- `services/user-service.js`: `sanitizeUserData` strips `password`, `auth_token` (by default), `registration_token`, `my_info_sg` from responses.

### Logout and session invalidation

- `controllers/user-controller.js`: `POST /users/logout` — body `email`, `authToken`; `userService.logout(email, authToken)`.
- `services/user-service.js`: `logout` — `User.findOne({ email, auth_token })`; skips clearing token if `authToken === process.env.SUPER_ADMIN_AUTH`; `invalidateUserCache(userId)` then `auth_token = null` and save.

### Request authentication pipeline

- `services/user-service.js`: `authMiddleware` — reads `Authorization` header and `app-origin`; M2M tokens from env allow list; `User.findOne` with `auth_token` or resolved `_id` from Auth0 / admin SSO JWT / `AuthTokenService`; optional Redis `getCachedUser` / `cacheUser` (TTL 15 min user, 1 h M2M); customer CDD suspension (`checkCddUserSuspended`) with path whitelist for `/users/me` exception pattern.

### Related routes in same controller (not the narrow “session” story but same file)

- `POST /users/login-with-sut` — exchanges single-use admin token (documented separately under openapi-tag-admin).
- `POST /users/reset-password` — password change triggers `invalidateUserCacheByUserId`.
