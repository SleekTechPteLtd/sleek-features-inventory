# Email verification

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Email address verification |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | New or updated-email user |
| **Business Outcome** | Confirmed contact channel for security and compliance |
| **Entry Point / Surface** | `EmailVerify`, `EmailVerification`, `EmailVerificationSent` in `sleek-auth-ui`; user verify endpoints on `sleek-auth` |
| **Short Description** | User follows link or enters code to mark email verified; optional resend |
| **Variants / Markets** | Per-tenant email branding |
| **Dependencies / Related Flows** | Registration; mail delivery |
| **Service / Repository** | `sleek-auth` (`user.controller` verify flows); `sleek-auth-ui` `src/features/auth/components/EmailVerify*.tsx` |
| **DB - Collections** | TBD |
| **Evidence Source** | Codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Must Keep |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/user/controllers/user.controller.ts` — verification-related routes (search `verify`, `email`).

### sleek-auth-ui

- `src/features/auth/components/EmailVerify.tsx`
- `src/features/auth/components/EmailVerification.tsx`, `EmailVerificationSent.tsx`
- `src/features/auth/hooks/useEmailVerification.tsx`

### sdk-auth-nest

- N/A.
