# User registration (self-service)

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Self-service user registration |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | New user creating an account before login |
| **Business Outcome** | Onboard users into Sleek identity without manual provisioning |
| **Entry Point / Surface** | `sleek-auth-ui` registration form; `sleek-auth` user registration endpoints (captcha-gated) |
| **Short Description** | Collects profile and credentials, verifies captcha server-side, creates user in identity provider stack |
| **Variants / Markets** | Country/client headers; optional invitation vs open registration (confirm with product) |
| **Dependencies / Related Flows** | Email verification; captcha; login |
| **Service / Repository** | `sleek-auth` (`user.controller` registration paths, `CaptchaService`); `sleek-auth-ui` (`RegistrationForm.tsx`) |
| **DB - Collections** | TBD |
| **Evidence Source** | Codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Must Keep |
| **Open Questions** | Which tenants allow public registration vs invite-only |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/user/controllers/user.controller.ts` — registration with `captchaService.verifyCaptcha`.
- `src/captcha/services/captcha.service.ts` — verification used by registration.

### sleek-auth-ui

- `src/features/auth/components/RegistrationForm.tsx`
- `src/features/auth/components/Captcha.tsx`

### sdk-auth-nest

- Registered users receive JWTs checked by standard guards (`nest-sdk-jwt-guards-and-context.md`).
