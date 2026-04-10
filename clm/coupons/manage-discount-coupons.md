# Manage Discount Coupons

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Discount Coupons |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations Admin, Sales Admin (BillingSuperAdmin / BillingOperationsAdmin / SalesAdmin groups); any authenticated user for read and referral-code lookup |
| **Business Outcome** | Enables billing and sales admins to create and manage discount coupons that reduce client invoice amounts, supporting promotions, client retention, and referral programs across scoped service groups. |
| **Entry Point / Surface** | Sleek Billings > Coupons (`/coupons`) |
| **Short Description** | Privileged admins create, edit, soft-delete, and review discount coupons (flat or percentage-based) with usage caps, expiry dates, applicable service groups, excluded service codes, and invoice scope controls. Any authenticated user can list coupons or fetch per-coupon usage history. A separate endpoint auto-creates a personal referral coupon on demand when the referral feature flag is enabled. |
| **Variants / Markets** | Unknown (platform-level excluded-service defaults vary by `PLATFORM` env var, but no explicit market gating in code) |
| **Dependencies / Related Flows** | Invoice generation (coupon applied at billing time); Referral Program flow (`referral_program` type auto-locks invoice scope to onboarding-only); Subscription Config API (`ServiceType` enum scopes applicable service groups); AppFeatureService / sleek-cms (feature flag `userReferral` gates referral-code creation); AuditLogsService (all mutations audit-logged) |
| **Service / Repository** | sleek-billings-backend; sleek-billings-frontend |
| **DB - Collections** | `coupons`, `couponusages` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which service writes to `couponusages` (i.e. what event increments currentUsage — invoice creation, payment, or coupon application)? Are there market-specific coupon restrictions beyond PLATFORM-based excluded-service defaults? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Backend files (sleek-billings-backend)
- `src/coupon/controllers/coupon.controller.ts` — REST controller at `/coupons`; CRUD guarded by `@GroupAuth(BillingSuperAdmin, BillingOperationsAdmin, SalesAdmin)`; read endpoints require `@Auth()` only
- `src/coupon/services/coupon.service.ts` — business logic: unique-code validation, soft-delete, maxUsage guard against currentUsage, referral-code auto-creation, audit logging via `AuditLogsService`
- `src/coupon/models/coupon.schema.ts` — `coupons` collection; unique sparse index on `userId` for `referral_program` type; soft-delete via `deletedAt` field
- `src/coupon/dtos/create-coupon.request.dto.ts` / `update-coupon.request.dto.ts` — validated fields: code, title, calculationType, type, amount, maxUsage (min 1), expiredAt (future date), applicableServiceGroups, excludedServices

### Backend API surface (`/coupons`)
| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| GET | `/coupons` | @Auth | Paginated list with currentUsage via `$lookup` on `couponusages` |
| GET | `/coupons/my-referral-code` | @Auth | Return (or auto-create) the caller's personal referral coupon |
| GET | `/coupons/:id` | @Auth | Fetch single coupon detail |
| GET | `/coupons/:id/usages` | @Auth | Paginated usage history for a coupon |
| POST | `/coupons` | @GroupAuth (SuperAdmin, OpsAdmin, SalesAdmin) | Create coupon; enforces code uniqueness |
| PUT | `/coupons/:id` | @GroupAuth (SuperAdmin, OpsAdmin, SalesAdmin) | Update coupon; blocks if maxUsage < currentUsage |
| DELETE | `/coupons/:id` | @GroupAuth (SuperAdmin, OpsAdmin, SalesAdmin) | Soft-delete (sets `deletedAt`) |

### Coupon data model (`coupons` collection)
| Field | Type / Values | Notes |
|---|---|---|
| `code` | String (uppercase) | Unique per active coupon (partial unique index with `deletedAt: null`) |
| `title` | String | Display label |
| `type` | `coupon` \| `referral_program` | One referral coupon per user enforced by sparse unique index on `userId` |
| `calculationType` | `flat` \| `percentage` | Determines discount math |
| `amount` | Number | Currency amount or percentage value |
| `maxUsage` | Number (`-1` = unlimited) | Enforced at update time against live usage count |
| `expiredAt` | Date | Must be a future date at creation |
| `applicableServiceGroups` | `ServiceType[]` | Scopes coupon to service groups (e.g. general, corporate-secretary) |
| `excludedServices` | `string[]` | Specific service codes excluded from discount |
| `applicableInvoiceType` | `allInvoices` \| `onboardingOnly` \| `renewalOnly` | Locked to `onboardingOnly` for referral_program type |
| `userId` | ObjectId (optional) | Owner of a referral coupon |
| `deletedAt` | Date (optional) | Soft-delete timestamp |

### Frontend files (sleek-billings-frontend)
- `src/pages/Coupons/CouponsList.jsx` — paginated list with debounced search by code/title, edit and delete actions
- `src/pages/Coupons/CouponForm.jsx` — shared create/edit form driven by declarative field config
- `src/services/api.js` — API calls to the `/coupons` backend resource
- `src/lib/constants.jsx` — `COUPON_CALCULATION_TYPE_OPTIONS` and `COUPON_APPLICABLE_SERVICE_GROUP_OPTIONS`

### Frontend routes
| Path | Component |
|---|---|
| `/coupons` | `CouponsList` |
| `/coupons/create` | `CouponForm` |
| `/coupons/edit/:id` | `CouponForm` |

### Related service integrations
- `@sleek-sdk/sleek-cms` `AppFeatureService.getAppFeature(AppFeature.userReferral)` — feature flag controlling referral coupon creation
- `AuditLogsService` — logs create, update, and delete coupon actions with old/new values
- `localStorage.billingConfig.COUPON_DEFAULT_EXCLUDED_SERVICE_CODES` (frontend) — pre-populates excluded services per platform on new coupon form
