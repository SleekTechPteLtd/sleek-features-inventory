# Captcha verification (abuse prevention)

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Server-side captcha verification on sensitive flows |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | End user submitting registration or similar forms |
| **Business Outcome** | Reduces automated abuse of public identity endpoints |
| **Entry Point / Surface** | `CaptchaService.verifyCaptcha` invoked from `user.controller` (e.g. registration); `Captcha.tsx` in UI |
| **Short Description** | Client supplies token; server validates with vendor before proceeding |
| **Variants / Markets** | Provider configuration per env |
| **Dependencies / Related Flows** | User registration |
| **Service / Repository** | `sleek-auth` `src/captcha/services/captcha.service.ts`, `user.controller.ts`; `sleek-auth-ui` `src/features/auth/components/Captcha.tsx` |
| **DB - Collections** | N/A |
| **Evidence Source** | Codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | TODOs in controller for expanded captcha coverage |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/captcha/services/captcha.service.ts`
- `src/user/controllers/user.controller.ts` — `verifyCaptcha` before registration.

### sleek-auth-ui

- `src/features/auth/components/Captcha.tsx`

### sdk-auth-nest

- N/A.
