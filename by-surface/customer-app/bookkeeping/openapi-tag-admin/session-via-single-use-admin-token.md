# Access user session via single-use admin token

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Access user session via single-use admin token |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, Admin, System (token issuance); customer account (session established without password) |
| **Business Outcome** | Authorized staff and partner flows can obtain a short-lived credential that is exchanged once for a normal user `auth_token`, enabling support, impersonation, and automation without sharing or storing the end user’s password. |
| **Entry Point / Surface** | Sleek Admin (and partner admin) flows that call the minting endpoints; exchange step via `POST /users/login-with-sut` (e.g. customer app or automation). Exact UI navigation not defined in code. |
| **Short Description** | Staff with the right permissions create an `AdminAuthenticationToken` row with a unique `single_use_token`, `for_user`, `requester`, optional `company`, and `expires_at`. The holder calls `login-with-sut` with that token; the service validates the record, ensures the target user has an `auth_token`, deactivates the single-use row, and returns the same `auth_token` shape as password login. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Depends on `userService.authMiddleware` and RBAC (`access_management` / `partner_access_management` / `companies` read) for minting; standard session usage thereafter (`Authorization` + `app-origin`). Partner path uses `partnerService.checkUserAccessToPartnerViaDomain`. Downstream: any API authenticated as the target user. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `adminauthenticationtokens` (Mongoose model `AdminAuthenticationToken`), `users` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether OpenAPI tag `admin` documents all three mint routes consistently; whether `expires_at` vs `moment().startOf('day')` in `loginWithSingleUseToken` is intentional (token minted with ~10s TTL but validity checked against calendar day start). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Customer exchange (no prior session)

- `controllers/user-controller.js`: `POST /users/login-with-sut` — validates `body.single_use_token`, calls `userService.loginWithSingleUseToken`, returns `{ auth_token }` or `422` with `AuthorizationError`.

### Core logic

- `services/user-service.js`: `loginWithSingleUseToken(singleUseToken)` — `AdminAuthenticationToken.findOne({ single_use_token, is_active: true, expires_at: { $gt: moment().startOf('day') } })`; loads `User` by `for_user` with `+auth_token`; generates `auth_token` on user if missing; sets `adminToken.is_active = false` and saves; returns `user.auth_token`. Exported on module exports.

### Minting (admin / partner)

- `controllers/admin/user-controller.js`:
  - `POST /admin/users/get-single-use-authentication-token-impersonation` — `userService.authMiddleware`, `accessControlService.can("access_management", "full")`; body `email` required; optional `cid` for `company`; resolves user by email or `temporary_email`; `AdminAuthenticationToken.create` with `single_use_token` from `userService.generateToken()`, `expires_at: moment().add(10, 'seconds')`, `requester: req.user`, etc.; returns `{ single_use_token }`.
  - `POST /admin/users/partner-get-sut` — `can("partner_access_management", "full")`; MS client user + domain check; creates token similarly; returns `{ single_use_token, on_load_page }`.
  - `POST /admin/users/get-single-use-authentication-token-dashboard` — `can("companies", "read")`; requires `cid`; creates token with optional company context.

### Schema

- `schemas/admin-auth-tokens.js`: Mongoose schema fields `for_user`, `requester`, `single_use_token` (unique, sparse index), `is_active`, `expires_at`, `company`; `timestamps: true`. Model name `AdminAuthenticationToken`.
