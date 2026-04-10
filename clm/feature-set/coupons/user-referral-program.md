# User Referral Program

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | User Referral Program |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Authenticated User (any logged-in Sleek customer) |
| **Business Outcome** | Enables a referral discount program where each user gets a unique personal coupon code they can share to earn referral benefits, driving customer acquisition through word-of-mouth incentives. |
| **Entry Point / Surface** | API `GET /coupons/my-referral-code` — likely surfaced in a Sleek App referral or account sharing page |
| **Short Description** | Returns the authenticated user's personal referral coupon code. If one does not yet exist, it is auto-generated on first access with a flat discount amount sourced from the CMS feature config (`user_referral`). Codes follow the format `REF<4 random chars>` and have a 10-year expiry. The feature is gated by a CMS-managed feature flag. |
| **Variants / Markets** | Unknown — platform-specific excluded services are configurable via `PLATFORM` env var, suggesting multi-market awareness (likely SG/HK), but active markets are not determinable from code alone |
| **Dependencies / Related Flows** | `@sleek-sdk/sleek-cms` AppFeatureService (feature flag `user_referral` must be enabled; discount amount sourced from CMS config); coupon application/redemption flow (when referred users use the code at checkout); `CryptoService` (random code generation); `AuditLogsService` (coupon CRUD audit trail) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `coupons`, `couponusages` |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium — feature is behind a CMS feature flag (`user_referral`); may not be active in all environments or markets |
| **Disposition** | Unknown |
| **Open Questions** | Which markets/platforms have this feature flag enabled? Is there a corresponding frontend surface that calls this endpoint? When a referred user redeems this code, is there a reward or credit-back flow for the referrer? What is the configured discount amount in CMS? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `coupon/controllers/coupon.controller.ts` — `GET /coupons/my-referral-code` handler `myReferralCode()`, guarded by `@Auth()` (any authenticated user, no admin group required)

### Service logic
- `coupon/services/coupon.service.ts` — `getMyReferralCode(userId: string)`:
  1. Fetches `AppFeature.userReferral` (`'user_referral'`) from `@sleek-sdk/sleek-cms` AppFeatureService; throws `BadRequestException` if not enabled.
  2. Queries `coupons` collection for an existing coupon owned by the requesting user (`{ userId }`).
  3. If none exists, auto-creates one via `couponRepository.create()` with:
     - `code`: `REF` + 4 random uppercase chars (collision-safe recursive generation via `CryptoService`)
     - `title`: `"Referral code"`
     - `calculationType`: `flat`
     - `type`: `referral_program`
     - `amount`: pulled from CMS feature config `value.discount`
     - `maxUsage`: `-1` (unlimited)
     - `expiredAt`: 10 years from creation (`REFERRAL_COUPON_EXPIRED_AT_DAYS = 3650`)
     - `applicableServiceGroups`: `[ServiceType.general]`
     - `excludedServices`: platform-specific list from `COUPON_DEFAULT_EXCLUDED_SERVICE_CODES[PLATFORM]`
  4. Returns the coupon document (existing or newly created).

### Constants
- `coupon/coupon.const.ts`:
  - `REFERRAL_COUPON_CODE_PREFIX = 'REF'`
  - `REFERRAL_COUPON_LENGTH = 4`
  - `REFERRAL_COUPON_EXPIRED_AT_DAYS = 10 * 365`

### Schema
- `coupon/models/coupon.schema.ts` — `Coupon` document on `coupons` collection:
  - `userId?: ObjectId` — referral code owner (the referrer)
  - `type: CouponType` — enum includes `referral_program`
  - Unique partial index: `{ userId: 1 }` where `type == 'referral_program'` — enforces one referral code per user
  - `couponusages` collection referenced via `$lookup` in `getCouponList` aggregation

### App feature gate
- `shared/consts/app-feature.const.ts` — `AppFeature.userReferral = 'user_referral'`
- Feature must be enabled in CMS and must carry a `value.discount` number for the flow to succeed
