# Review company user KYC activity

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Review company user KYC activity |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Sleek Admin (primary); product intent includes the end user subject to the same KYC history — see Open Questions |
| **Business Outcome** | Admins and compliance stakeholders can see a chronological, human-readable trail of KYC-related events for a person across companies, for audit and regulatory review. |
| **Entry Point / Surface** | Sleek API: `POST` `/v2/company-users/kyc-activity/{userId}` (OpenAPI tag `kyc-activity`, `public/api-docs/company-user.yml`); authenticated via `userService.authMiddleware` and `adminOrLoggedCompanyUserAuthMiddleware` |
| **Short Description** | Loads all `CompanyUser` records for a given user and selected companies, walks embedded `kyc_history`, maps each entry to display copy and purpose (incorporation vs KYC refresh) using admin app feature `kyc_activity`, filters by date range and purpose, merges and sorts activities, and returns items plus the user profile. History is appended elsewhere via `updateCompanyUserKycHistory`. |
| **Variants / Markets** | SG, HK, UK |
| **Dependencies / Related Flows** | `app-features-util` (`kyc_activity` admin config: remarks, statuses, content templates), `User` lookups for admin names on approved steps, KYC flows that call `updateCompanyUserKycHistory` (invitations, KYC refresh, auto-verify, Camunda, scripts) |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companyusers` (`kyc_history` array, `kyc_status`, `invitation_status`, `kyc_refresh`, populated `user`/`company`), `users` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `adminOrLoggedCompanyUserAuthMiddleware` resolves the non-admin path with `req.params.companyUserId`, but this route defines `{userId}`. Confirm whether non–Sleek Admin access (e.g. the company user viewing their own trail) is intended and working, or admin-only in practice. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Router** (`controllers-v2/company-user.js`): `buildPostRouteAdminOnly("/kyc-activity/:userId", …getKycActivity)` — `POST` with `userService.authMiddleware` and `adminOrLoggedCompanyUserAuthMiddleware` (Sleek Admin passes; non-admin path checks `companyUserId` per middleware implementation).
- **Handler / service** (`services/company-user-kyc-history.js`):
  - `getKycActivity` — reads `userId` from params; body: `sort`, `dateFrom`, `dateTo`, `companyIds`, `purposesOfKyc`; loads `kyc_activity` feature config; `CompanyUser.find({ user: userId, company: { $in: companyIds } }).populate(["user","company"])`.
  - `getKycActivityFromCompanyUser` — filters `kyc_history` by date range; tracks post-refresh context after `REFRESH_TRIGGERED`; builds activities with `getKycActivityContentAndPurpose` (remarks for MyInfo/Onfido, approved, refresh triggered, submit refresh, auto-verify, etc.); marks latest item `isLatest`.
  - `updateCompanyUserKycHistory` — pushes to `companyUser.kyc_history` (optional invitation status snapshot), `save()` — used by invitations, KYC refresh, auto-verify, Camunda handlers, and scripts.
- **Schema** (`schemas/company-user.js`): `kyc_history` as `Array`; `kyc_status`, `invitation_status`, `kyc_refresh`, timestamps on company user document.
- **API docs** (`public/api-docs/company-user.yml`): path `/v2/company-users/kyc-activity/{userId}`, tag `kyc-activity`, schema `KYCActivityResponse`.
- **Tests** (`tests/controllers-v2/company-user/get-kyc-activity.js`): `POST /v2/company-users/kyc-activity/:userId` with admin auth and sample `kyc_history` rows.
