# Authentication (category)

**Proving identity, issuing credentials, and propagating auth in services** — everything a user or machine does to *become recognized* before fine-grained “can they do X?” logic runs.

Includes: hosted login / PKCE / OAuth, registration, password & email recovery, MFA, OAuth client + M2M token issuance, captcha and T&C gates on auth flows, **Nest guards that validate JWTs / M2M tokens** (the SDK side of authentication), and **admin/support “login as”** where it is a distinct product capability (see [admin-login-as-customer-single-use-token.md](./admin-login-as-customer-single-use-token.md)).

Authorization (policies, roles, assignments, AuthZ PDP) lives in [../authorization/](../authorization/).

## Scope (no duplicate auth rows)

**Sleek Auth** (`sleek-auth` + `sleek-auth-ui` + `sdk-auth-nest`) is the **canonical** stack for authentication capability rows. Do **not** add parallel master-sheet rows for legacy **sleek-back** / **customer-mfe** / **sleek-website** (admin) login, OTP, password reset, or registration — those are the old path. When scanning those repos, cite legacy endpoints only as **migration / dependency notes** inside other docs or ADRs, not as separate “Authentication” features alongside Sleek Auth.

**Exception:** [admin-login-as-customer-single-use-token.md](./admin-login-as-customer-single-use-token.md) is a single **Platform** row for staff **impersonation / login-as** (legacy implementation + **Sleek Auth gap**). It is not a second “customer login” feature; it tracks parity work for Sleek Auth.

## Capability documents

| Document | Short description |
|----------|-------------------|
| [hosted-login-oauth-pkce.md](./hosted-login-oauth-pkce.md) | Login, PKCE/OAuth, prepare-auth, SSO |
| [token-m2m-and-refresh.md](./token-m2m-and-refresh.md) | M2M client credentials, refresh tokens |
| [user-registration.md](./user-registration.md) | Self-service registration (captcha-gated) |
| [password-recovery.md](./password-recovery.md) | Forgot / reset password |
| [email-verification.md](./email-verification.md) | Email verification |
| [multi-factor-authentication.md](./multi-factor-authentication.md) | MFA API + UI hooks |
| [captcha-verification.md](./captcha-verification.md) | Captcha on sensitive public routes |
| [cross-country-terms-acceptance.md](./cross-country-terms-acceptance.md) | T&C gating in login / PKCE |
| [oauth-client-management.md](./oauth-client-management.md) | Register OAuth clients, secrets, PKCE URL helpers |
| [nest-sdk-jwt-guards-and-context.md](./nest-sdk-jwt-guards-and-context.md) | Verify JWT, `@Authenticated()`, request context |
| [nest-sdk-m2m-flexible-auth.md](./nest-sdk-m2m-flexible-auth.md) | M2M / flexible auth guards |
| [admin-login-as-customer-single-use-token.md](./admin-login-as-customer-single-use-token.md) | Admin “login as” / SUT; legacy + **not in Sleek Auth yet** |

## UI surfaces (sleek-auth-ui) — quick map

| Area | Typical paths | Doc |
|------|----------------|-----|
| Login, PKCE, authorize callbacks | `src/features/auth/components/LoginForm.tsx`, `PkceCallbackHome.tsx`, `AuthorizeCallback.tsx` | hosted-login-oauth-pkce |
| Registration + captcha widget | `RegistrationForm.tsx`, `Captcha.tsx` | user-registration, captcha-verification |
| Password reset | `ForgotPasswordPage.tsx`, `ResetPasswordPage.tsx` | password-recovery |
| Email verify | `EmailVerify*.tsx`, `useEmailVerification.tsx` | email-verification |
| MFA | `MfaHome.tsx`, `MfaForm.tsx`, `CodeBasedMfaForm.tsx`, `MfaContext.tsx` | multi-factor-authentication |
| Cross-country T&C | `CrossCountryTCModal.tsx` | cross-country-terms-acceptance |
