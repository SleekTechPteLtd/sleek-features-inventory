# Cross-country terms and conditions acceptance

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Accept terms when login crosses country / compliance context |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | User blocked at login until T&C accepted |
| **Business Outcome** | Meets regional/legal gating before session establishment |
| **Entry Point / Surface** | Login/PKCE flow returning pending-TC state; `CrossCountryTCModal` in UI; `AcceptTcDto` on API |
| **Short Description** | Server detects pending acceptance; UI presents modal; user confirms to continue auth |
| **Variants / Markets** | Country-specific rules |
| **Dependencies / Related Flows** | Hosted login; consent persistence (`consent` module entities in sleek-auth) |
| **Service / Repository** | `sleek-auth` login flow (`AcceptTcDto`, PKCE service pending responses); `sleek-auth-ui` `CrossCountryTCModal.tsx` |
| **DB - Collections** | Consent records (see `src/consent/entities/`) |
| **Evidence Source** | Codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Must Keep |
| **Open Questions** | Exact jurisdictions and copy ownership (legal vs product) |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/login/dto/accept-tc.dto.ts`
- `src/login/services/pkce.service.ts` — `PendingTCResponse` (see login controller imports).
- `src/consent/` — entities/repository for persistence.

### sleek-auth-ui

- `src/features/auth/components/CrossCountryTCModal.tsx`

### sdk-auth-nest

- N/A.
