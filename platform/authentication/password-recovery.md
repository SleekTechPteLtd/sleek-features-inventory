# Password recovery (forgot / reset)

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Forgot password and reset password |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | User who lost password |
| **Business Outcome** | Self-service account recovery without support tickets |
| **Entry Point / Surface** | `ForgotPasswordPage`, `ResetPasswordPage` in `sleek-auth-ui`; user APIs on `sleek-auth` |
| **Short Description** | Request reset link/token, validate token, set new password per policy |
| **Variants / Markets** | Email delivery templates; token TTL |
| **Dependencies / Related Flows** | Login; email infrastructure |
| **Service / Repository** | `sleek-auth` (`user.controller` reset/validate routes); `sleek-auth-ui` pages under `features/auth/pages/` |
| **DB - Collections** | TBD |
| **Evidence Source** | Codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/user/controllers/user.controller.ts` — reset password, validate reset token (see module docs strings).

### sleek-auth-ui

- `src/features/auth/pages/ForgotPasswordPage.tsx`
- `src/features/auth/pages/ResetPasswordPage.tsx`

### sdk-auth-nest

- N/A (post-reset login uses JWT verification).
