# Verify identity with OTP (sign-in and onboarding)

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Verify identity with OTP (sign-in and onboarding) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | End user, invitee (customer); Operations / support (via escalation emails and audit) |
| **Business Outcome** | Users prove control of SMS or email during login, registration, and onboarding so Sleek can reduce account takeover and meet trust requirements for sensitive flows. |
| **Entry Point / Surface** | Customer web and app flows that require MFA: login (including password-then-OTP), registration and email verification, post-payment onboarding identity steps, and invitation acceptance — backed by API routes under `/v2/two-factor-auth`. |
| **Short Description** | Sends one-time codes via SMS or email through the Sleek OTP service, enforces resend cooldowns and verification attempt limits, applies temporary then permanent blocks with support notification and audit on repeated failures, optionally returns a business-account JWT after successful verification when configured, exposes whether OTP is enabled for an email, and issues a session token after password validation for 2FA login handoff. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Sleek OTP** HTTP API (`OtpVendor`, `/otp/send`, `/otp/verify`); **mailer** (email OTP template, verify-email, 2FA support template); **CMS / app features** (`appFeatureUtil` for retries, cooldowns, block duration, UI flags); **partner** context for branded verify links; **business-account-service** optional `postSkipOTPValidationAndGetSignedJwt` (SBA JWT); **sleek auditor** HTTP API for user-block audit events; **auth** helpers (`getMfaConfig`, `getUserDefaultMfaChannel`, `isUserMfaReachedMaxSends`). Related: OAuth/MFA flows in `auth-service.js` use `TwoFactorAuthService` MFA APIs separately from this controller path. |
| **Service / Repository** | sleek-back; external: sleek-otp, sleek-mailer (via mailer), sleek-auditor |
| **DB - Collections** | `users` (User); `companyusers` (CompanyUser — invitation token for new invitation OTP flow) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Routes (`app-router.js` mounts router at `/v2/two-factor-auth`)

- `controllers-v2/two-factor-authentication.js`: `POST :userId/send-otp`, `POST :userId/validate-otp/`, `POST :userId/onboarding-validate-otp/`, `POST :userId/update-otp-config` (with `userService.authMiddleware`), `POST check-otp-enabled` (with `authMiddleware`), `POST get-login-auth`.

### Handlers (`controllers-v2/handlers/two-factor-authentication/otp-methods.js`)

- **sendOtpCodeToUser**: Loads user; optional `isLogin` clears `authToken`; resolves phone from body or user; `authHelpers.getUserDefaultMfaChannel` for SMS vs email; `TwoFactorAuthService.sendOtp`; `getOTPStatus` returns masked contact, `next_resend`, channel, expiry, remaining attempts (feature-flagged shapes for new registration UI vs legacy).
- **sendOtpCodeToUserMiddleware** / **validateOtpCodeMiddleware**: Block when temporarily or permanently blocked; validate middleware also checks OTP expiry; send middleware calls `authHelpers.isUserMfaReachedMaxSends` and can permanently block for “Multiple Resend Attempts”.
- **validateOtpCode**: `twoFactorAuthService.verifyOtp`; on success resets 2FA fields, `invalidateUserCacheByUserId`; unregistered users get verify-email; new invitation flow can set `CompanyUser.invitation_token`; optional `sba_token` from `businessAccountService.postSkipOTPValidationAndGetSignedJwt` when `business_account.sba_skip_2fa_first_attempt` is enabled; on failure decrements attempts, then temporary block or permanent block with `sendCustomerSupportEmail` (template `TWO_FACTOR_AUTHENTICATION_SUPPORT`) and `saveAuditLog` / `buildUserAuditLog` (`two_factor_authentication_user_blocked`).
- **validateOnboardingOtpCode**: Same verification and block logic with onboarding-specific OTP action labelling (`ONBOARDING_OTP`).
- **updateTwoFactorAuthenticationConfig**: Authenticated updates to enabled, blocked, channel, and admin unblock paths.
- **checkIfOtpEnabled**: Returns `user.two_factor_authentication_enabled` for query `email`.
- **getLoginAuth**: Clears OTP fields on user, then `userService.loginKeep` to return `auth_token` after password check (password-to-session for 2FA login).

### Services

- `services/two-factor-auth-service.js`: `getConfig` from CMS (`retries`, `expiry_time`, `send_attempts`, `resend_buffer_time`, admin OTP message); `sendOtp` / `verifyOtp` delegate to `OtpVendor`; also exposes MFA token APIs (`initMfa`, `challengeMfa`, `verifyChallenge`) used elsewhere.
- `services/user-service.js`: `authMiddleware` (routes that require it); `loginKeep` (password verification and session token issuance); `invalidateUserCacheByUserId` after OTP-related user updates; `generateToken` used for invitation tokens.

### External integration (`vendors/otp-vendor.js`)

- `sendOtp`: POST `/otp/send` to Sleek OTP; stores base64 `two_factor_verification_token` with context, sets `two_factor_authentication_code_expiry`, `two_factor_authentication_last_resend`, increments send attempts; respects resend buffer vs previous token.
- `verifyOtp`: POST `/otp/verify` with verification token and code; clears token on success.

### Schema (`schemas/user.js`)

- Fields include `two_factor_authentication_enabled`, `two_factor_number_verified`, `two_factor_authentication_code` / `_expiry`, `two_factor_authentication_remaining_attempts`, temporary and permanent block flags and reasons, `two_factor_authentication_channel`, `two_factor_verification_token`, `two_factor_authentication_last_resend`, `two_factor_authentication_send_attempts`.
