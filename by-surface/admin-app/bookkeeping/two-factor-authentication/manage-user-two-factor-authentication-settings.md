# Manage user two-factor authentication settings

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage user two-factor authentication settings |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | End user (OTP send, validate, login handoff); authenticated caller for `update-otp-config` and `check-otp-enabled` (intended operators or self-service — not fully determined in cited files) |
| **Business Outcome** | Organizations can require and recover multi-factor access: users prove possession of email or SMS OTP, and authorized processes can align policy (2FA on/off, block state, channel, OTP reset) without leaving stale codes or cache. |
| **Entry Point / Surface** | Sleek web flows and internal tools consuming sleek-back HTTP API under base path `POST /v2/two-factor-auth/...` (see Evidence). Exact admin or app navigation labels are not defined in the referenced files. |
| **Short Description** | Exposes OTP delivery and verification (`TwoFactorAuthService` + vendor), temporary and permanent lockout after failed attempts (CMS-driven retries and windows), support notification and audit on hard block, and a configurable `update-otp-config` path that toggles `two_factor_authentication_enabled`, block/unblock with reasons and timestamps, and `two_factor_authentication_channel`, clearing or restoring OTP-related fields when unblocking. User cache is invalidated after material user document changes. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **OTP**: `services/two-factor-auth-service.js` → OTP vendor. **CMS**: `appFeatureUtil` profile `two_factor_authentication` (retries, temporary block duration, action labels). **Mail**: `mailerVendor` (support on block), `mailerService` (verify email on some paths). **Partner/origin**: `partner-service`, `getPartnerByDomainUrl`. **SBA**: `businessAccountService.postSkipOTPValidationAndGetSignedJwt` when CMS `business_account.sba_skip_2fa_first_attempt`. **Audit**: `saveAuditLog` / `buildUserAuditLog`. **Cache**: `userService.invalidateUserCacheByUserId` → Redis user cache. **Login**: `userService.loginKeep` in `getLoginAuth`. **Related policy**: `user-service` user-update sanitization allows `phone` only when 2FA is off or KYC path applies. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `users` (two-factor and block fields per `schemas/user.js`); `companyusers` (invitation token on some invitation OTP paths). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `update-otp-config` is restricted to operators vs self-service: handler uses `authMiddleware` but does not compare `req.user` to `:userId` in the cited code. Which persistence store backs `saveAuditLog` for `two_factor_authentication_user_blocked`. Market-specific behaviour beyond tenant CMS — not enumerated in cited files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `app-router.js`

- **`/v2/two-factor-auth`** — mounts `controllers-v2/two-factor-authentication`.

### `controllers-v2/two-factor-authentication.js`

- **`POST /:userId/send-otp`** — `sendOtpCodeToUserMiddleware`, `sendOtpCodeToUser`.
- **`POST /:userId/validate-otp/`** — `validateOtpCodeMiddleware`, `validateOtpCode`.
- **`POST /:userId/onboarding-validate-otp/`** — `validateOtpCodeMiddleware`, `validateOnboardingOtpCode`.
- **`POST /:userId/update-otp-config`** — `userService.authMiddleware`, `updateTwoFactorAuthenticationConfig`.
- **`POST /check-otp-enabled`** — `userService.authMiddleware`, `checkIfOtpEnabled` (uses `req.query.email`).
- **`POST /get-login-auth`** — `getLoginAuth` (no `authMiddleware` on this route in the router file).

### `controllers-v2/handlers/two-factor-authentication/otp-methods.js`

- **`sendOtpCodeToUser`** — Loads `User` by id; optional login path clears `authToken`; resolves phone/channel via `authHelpers.getUserDefaultMfaChannel`; `TwoFactorAuthService.sendOtp`; may persist `two_factor_authentication_channel`; `userService.invalidateUserCacheByUserId` when channel changes; returns masked status via `getOTPStatus` (CMS `new_registration_ui`, partner host).
- **`validateOtpCode` / `validateOnboardingOtpCode`** — `TwoFactorAuthService.verifyOtp`; on success resets attempts, codes, expiry, temporary/permanent block flags, `two_factor_number_verified`, optional verify-email and SBA token branch; on failure decrements `two_factor_authentication_remaining_attempts`, applies temporary then permanent block, `sendCustomerSupportEmail` (template `TWO_FACTOR_AUTHENTICATION_SUPPORT`), `saveAuditLog` with `two_factor_authentication_user_blocked`.
- **`updateTwoFactorAuthenticationConfig`** — Body: `twoFactorAuthenticationEnabled`, `twoFactorAuthenticationBlocked`, `reasons`, `twoFactorAuthenticationChannel`. Updates `user` two-factor fields (block timestamps/reasons, unblock timestamps/reasons, full reset of OTP state on unblock per code path); `userService.invalidateUserCacheByUserId`.
- **`checkIfOtpEnabled`** — Returns `user.two_factor_authentication_enabled` for email lookup.
- **`getLoginAuth`** — Clears OTP code fields on user, then `userService.loginKeep` with client type from origin (`SLEEK_CLIENT` vs `MS_CLIENT`), returns `auth_token`.
- **Middleware** — `validateOtpCodeMiddleware` / `sendOtpCodeToUserMiddleware` enforce temporary block window, permanent block message, expiry; send path can block on max resends via `authHelpers.isUserMfaReachedMaxSends`.

### `services/user-service.js`

- **`authMiddleware`** — Used on `update-otp-config` and `check-otp-enabled` (Bearer / Auth0 / admin SSO / M2M per implementation).
- **`invalidateUserCacheByUserId`** — Called after 2FA-related `user.save()` paths in `otp-methods.js` so Redis-backed user cache reflects updated MFA state.
- **`loginKeep`** — Invoked from `getLoginAuth` to obtain `authToken` after OTP preconditions.
- **User update sanitation** (context) — When sanitizing customer self-updates, `phone` is only allowed if `!user.two_factor_authentication_enabled && !hasKycSubmission` (alongside other fields), linking profile edit policy to 2FA state.

### `schemas/user.js` (fields referenced by flows)

- `two_factor_authentication_enabled`, `two_factor_number_verified`, `two_factor_authentication_code`, `two_factor_authentication_code_expiry`, `two_factor_authentication_remaining_attempts`, `two_factor_authentication_temporary_blocked`, `two_factor_authentication_temporary_blocked_expiry`, `two_factor_authentication_blocked`, `two_factor_authentication_blocked_at`, `two_factor_authentication_blocked_reasons`, `two_factor_authentication_unblocked_at`, `two_factor_authentication_unblocked_reasons`, `two_factor_authentication_channel`, `two_factor_authentication_last_resend`, `two_factor_authentication_send_attempts`.
