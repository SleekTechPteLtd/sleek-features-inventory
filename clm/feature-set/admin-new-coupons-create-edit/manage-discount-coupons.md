# Manage Discount Coupons

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Discount Coupons |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Enables admins to create and configure discount coupons that clients can apply at checkout to reduce payment amounts across specific service categories. |
| **Entry Point / Surface** | Sleek Admin Portal > Admin > New Coupons > Create / Edit Coupon (`/admin/new-coupons/create-edit`) |
| **Short Description** | Admins create new coupons or update existing ones, setting the coupon code, title, discount type (flat or percentage), discount amount, usage cap, expiry date, applicable service categories, and individually excluded services. Submissions are persisted via the payment-api microservice. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Admin Coupon List (`/admin/new-coupons`); payment-api.sleek.sg (coupon CRUD); `utils/api.js getServices()` (populates excluded-services dropdown) |
| **Service / Repository** | sleek-website, payment-api (payment-api.sleek.sg) |
| **DB - Collections** | Unknown (managed by payment-api; not visible from frontend) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets/jurisdictions are coupons available in — no market-gating logic visible in the frontend. Is `admin: true` flag enforcing backend auth, or is there separate middleware on payment-api? What DB/collection does payment-api use to persist coupons? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/views/admin/new-coupons/create-edit.js` — `AdminCouponsCreateEditView` React component; dual-mode (create vs. edit) driven by `?couponId` query param
- `src/utils/payment-api.js` — HTTP client wrappers targeting `payment-api.sleek.sg`
- `src/utils/constants.js` — `NEW_COUPON_APPLICABLE_SERVICES` list

### Form fields
| Field | Type | Notes |
|---|---|---|
| `code` | text (required) | Coupon redemption code |
| `title` | text (required) | Human-readable label |
| `calculationType` | select | `flat` or `percentage` |
| `amount` | number (required) | Discount value |
| `maxUsage` | number (required) | Cap on total redemptions |
| `expiredAt` | date (required) | End of day ISO timestamp sent to API |
| `applicableServiceGroups` | multi-select | From `NEW_COUPON_APPLICABLE_SERVICES`: `general`, `accounting`, `accounting-add-on`, `corpsec`, `corpsec-add-on`, `corporate_secretary`, `immigration`, `mailroom`, `business_account` |
| `excludedServices` | multi-select | Populated from `api.getServices()` — individual service codes/names |

### API calls (payment-api.sleek.sg)
- `GET  /coupons/:id` — `paymentApi.getCouponDetail(couponId)` — pre-fills form in edit mode
- `POST /coupons` — `paymentApi.createCoupon({body, admin: true})` — creates new coupon
- `PUT  /coupons/:id` — `paymentApi.updateCoupon(couponId, {body, admin: true})` — updates existing coupon
- `GET  /services` (via `api.getServices`) — fetches all services to populate excluded-services dropdown

### Auth surface
- `getUser()` / `checkResponseIfAuthorized` — session-based auth check on mount; redirects to `/verify/` if email unverified
- `admin: true` flag passed as query/body option on create/update calls — backend enforcement assumed on payment-api
