# Multi-factor authentication (Sleek Auth MFA)

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | MFA enrollment, challenge, and factor management |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Authenticated user in MFA session |
| **Business Outcome** | Stronger account protection via second factors |
| **Entry Point / Surface** | `GET/POST /mfa/*` under `ClientAndTenantGuard`; `sleek-auth-ui` `MfaHome`, `MfaForm`, `CodeBasedMfaForm`, `MfaContext` |
| **Short Description** | MFA session gates status, challenge, list/enroll/unenroll factors; integrates provider-agnostic MFA service |
| **Variants / Markets** | Factor types supported by configured providers |
| **Dependencies / Related Flows** | Login (step-up); hosted auth error pages (`MfaErrorPage`) |
| **Service / Repository** | `sleek-auth` (`mfa.controller`, `MfaProviderAgnosticService`, guards/decorators); `sleek-auth-ui` `src/features/auth/components/Mfa*.tsx` |
| **DB - Collections** | TBD |
| **Evidence Source** | Codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Must Keep |
| **Open Questions** | Parity with legacy sleek-back OTP (`/v2/two-factor-auth`) |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/mfa/controllers/mfa.controller.ts` — `status`, `challenge`, `factors`, enroll/unenroll, verify.
- `src/mfa/services/mfa-provider-agnostic.service.ts`
- `src/mfa/decorators/mfa-session-guard.decorator.ts`

### sleek-auth-ui

- `src/features/auth/components/MfaHome.tsx`, `MfaForm.tsx`, `CodeBasedMfaForm.tsx`
- `src/features/auth/contexts/MfaContext.tsx`
- `src/features/auth/pages/MfaErrorPage.tsx`
- `src/features/auth/hooks/useMfaHelper.tsx`

### sdk-auth-nest

- Optional MFA claims in JWT handling where applicable (`AuthService` / payload types in `src/types/`).
