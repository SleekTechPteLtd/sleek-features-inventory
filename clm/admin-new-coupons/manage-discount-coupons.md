# Manage Discount Coupons

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Discount Coupons |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Enables admins to create and maintain discount coupons that can be applied to client invoices, controlling how and when discounts are granted across Sleek's service offerings. |
| **Entry Point / Surface** | Sleek Admin Panel > New Coupons (`/admin/new-coupons`) |
| **Short Description** | Admins can list, create, edit, and delete discount coupons. Each coupon has a code, title, calculation type (flat or percentage), discount amount, maximum usage cap, expiry date, applicable service groups, and an optional excluded-services list. Usage count per coupon is tracked live against the cap. |
| **Variants / Markets** | SG, HK (currency symbol is platform-config driven; service groups include `immigration`, `business_account`, and other multi-market services) |
| **Dependencies / Related Flows** | Payment Service (coupon CRUD + usage endpoints); `api.getServices` for the excludable services list; `getPlatformConfig` for currency symbol; client-facing coupon redemption flow (not in this module) |
| **Service / Repository** | sleek-website (frontend), payment-service (backend API at `getBasePaymentServiceUrl()`) |
| **DB - Collections** | Unknown (owned by payment-service; collection name not visible from frontend code) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which roles/permission levels map to `user.permissions.coupons === "full"`? Are coupons applied automatically at checkout or manually by admins? Does the payment-service enforce the `maxUsage` cap server-side, or is it advisory? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry points
- `views/admin/new-coupons/index.js` — `AdminNewCouponsView`: paginated list of coupons with sortable/filterable columns (code, title, calculation type, amount, current usage / max usage, applicable service groups, created at, expired at). Edit and Remove buttons are disabled when `user.permissions.coupons !== "full"` or when coupon `status !== "new"`.
- `views/admin/new-coupons/create-edit.js` — `AdminCouponsCreateEditView`: single-page form for creating or updating a coupon. Distinguishes create vs. update via `?couponId=` query param.

### Coupon data model (fields visible in forms)
| Field | Type | Notes |
|---|---|---|
| `code` | string | Unique coupon code entered at checkout |
| `title` | string | Human-readable label |
| `type` | string | Always `"coupon"` (hardcoded) |
| `calculationType` | enum | `"flat"` (currency amount) or `"percentage"` |
| `amount` | number | Discount value in the selected calculation type |
| `maxUsage` | number | Total redemption cap |
| `expiredAt` | date | End-of-day expiry; max set 99 years from now |
| `applicableServiceGroups` | string[] | Multi-select from `NEW_COUPON_APPLICABLE_SERVICES` constant |
| `excludedServices` | string[] | Specific services (by code) excluded from discount |

### Applicable service groups (from `constants.js:2504`)
`general`, `accounting`, `accounting-add-on`, `corpsec`, `corpsec-add-on`, `corporate_secretary`, `immigration`, `mailroom`, `business_account`

### API calls (via `utils/payment-api.js`)
| Operation | Method | Endpoint |
|---|---|---|
| List coupons | GET | `{paymentServiceUrl}/coupons` (paginated, filterable, sortable) |
| Get coupon detail | GET | `{paymentServiceUrl}/coupons/:id` |
| Get coupon usages | GET | `{paymentServiceUrl}/coupons/:id/usages` |
| Create coupon | POST | `{paymentServiceUrl}/coupons` |
| Update coupon | PUT | `{paymentServiceUrl}/coupons/:id` |
| Delete coupon | DELETE | `{paymentServiceUrl}/coupons/:id` |

### Auth / permission guard
- Session auth enforced via `api.getUser()` + `checkResponseIfAuthorized`; email verification required.
- Mutation actions (create, edit, delete) require `user.permissions.coupons === "full"`.
- Edit/Remove are additionally disabled when coupon `status !== "new"` (immutable once progressed).

### Supporting utilities
- `utils/payment-api.js` — all coupon HTTP calls
- `utils/constants.js:2504` — `NEW_COUPON_APPLICABLE_SERVICES` enum
- `utils/config-loader.js` — `getPlatformConfig()` for currency symbol (platform-aware)
- `utils/auth-utils.js` — `checkResponseIfAuthorized` redirect guard
- `layouts/new-admin` — shared admin shell (sidebar key `"new-coupons"`)
