# Issue impersonation and support access tokens

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Issue impersonation and support access tokens |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin, Operations User (Sleek); partner staff with partner access management for MS client flows |
| **Business Outcome** | Authorized internal and partner-domain staff can obtain a target user’s session credential (full `auth_token` or a short-lived single-use token) to troubleshoot, support, or act as that user without password sharing. |
| **Entry Point / Surface** | Sleek Admin API routes under `/admin/users/…` (exact UI not defined in these handlers). Partner path requires `email`, `domain`, and an MS client user. |
| **Short Description** | Admins with `access_management` (or `companies` read for company-scoped dashboard access, or `partner_access_management` for partner flows) mint `AdminAuthenticationToken` rows for impersonation or dashboard handoff, or read or ensure a user’s persisted `auth_token` via dedicated endpoints. Single-use tokens expire quickly and are consumed via `loginWithSingleUseToken` elsewhere. Partner minting validates domain access through `checkUserAccessToPartnerViaDomain` before issuing the token. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Token exchange after mint: `POST /users/login-with-sut` → `userService.loginWithSingleUseToken` (see `accounting/openapi-tag-admin/session-via-single-use-admin-token.md`). Partner resolution: `partnerService.checkUserAccessToPartnerViaDomain`, `Partner` / `User` (MS client) linkage. Downstream: any API authenticated with the returned `Authorization` value. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `adminauthenticationtokens` (model `AdminAuthenticationToken`), `users` (field `auth_token`, selectively exposed) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `loginWithSingleUseToken` use of `moment().startOf('day')` vs minted `expires_at` (~10s) is fully intentional; operational policy for `get-authtoken` vs SUT-only flows. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Full `auth_token` surfaces (support / session continuity)

- `controllers/admin/user-controller.js`: `POST /admin/users/get-authtoken` — `userService.authMiddleware`, `accessControlService.can("access_management", "full")`; body `email`; `User.findOne({ email }).select("+auth_token")`; returns `{ auth_token }`.
- `controllers/admin/user-controller.js`: `GET /admin/users/:userId` — with query `fields` including `auth_token`, selects `+auth_token`, generates and saves a new token via `userService.generateToken()` if absent; `userService.sanitizeUserData(user, !includeAuthToken)` controls exposure.

### Single-use token minting (impersonation, dashboard, partner)

- `controllers/admin/user-controller.js`: `POST /admin/users/get-single-use-authentication-token-impersonation` — `can("access_management", "full")`; body `email` (user resolved by `email` or `temporary_email`); optional `cid` → `company` on token; `userService.generateToken()`, `expires_at: moment().add(10, 'seconds')`; `AdminAuthenticationToken.create({ single_use_token, for_user, requester: req.user, is_active, expires_at, company })`; returns `{ single_use_token }`.
- `controllers/admin/user-controller.js`: `POST /admin/users/get-single-use-authentication-token-dashboard` — `can("companies", "read")`; body `cid` required; resolves user by email (defaults to `req.user.email` if omitted in validation path — branch uses `bodyCleaned.email`); same mint pattern with `company: companyId`; returns `{ single_use_token }`.
- `controllers/admin/user-controller.js`: `POST /admin/users/partner-get-sut` — `can("partner_access_management", "full")`; body `email`, `domain`; `User` must be `CLIENT_TYPE.MS_CLIENT`; `partnerService.checkUserAccessToPartnerViaDomain(user, domain)` yields `on_load_page`; `AdminAuthenticationToken.create` (no `company` in create call); returns `{ single_use_token, on_load_page }` or partner error codes.

### Consumption of single-use tokens (not in this controller; dependency)

- `services/user-service.js`: `loginWithSingleUseToken(singleUseToken)` — loads active `AdminAuthenticationToken`, ensures target user `auth_token`, deactivates token, returns `user.auth_token`.

### Schema

- `schemas/admin-auth-tokens.js`: `for_user`, `requester`, `single_use_token` (unique, sparse index), `is_active`, `expires_at`, optional `company` ref; timestamps.

### Partner domain gate

- `services/partners/partner-service.js`: `checkUserAccessToPartnerViaDomain(user, domain)` — resolves `Partner` by `domain_url` or `admin_domain_url`, ensures `User` belongs to that partner, returns dashboard route hint by `partner_type` (`MS_PARTNER_ADMIN` vs other).
