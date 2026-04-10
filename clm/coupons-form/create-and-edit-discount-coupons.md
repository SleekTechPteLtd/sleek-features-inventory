# Create and Edit Discount Coupons

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Create and Edit Discount Coupons |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators define discount coupons with precise targeting rules (discount type, usage cap, expiry, service scope, invoice scope) so validated discounts can be applied to client billing. |
| **Entry Point / Surface** | Sleek Billings Admin > Coupons > Create (`/coupons/create`) or Edit (`/coupons/edit/:id`) |
| **Short Description** | A shared create/edit form lets operators configure a coupon's code, title, calculation type (flat or percentage), discount amount, usage cap, expiry date, applicable service groups, individually excluded service codes, and invoice type scope (all invoices, onboarding-only, or renewal-only). On create, default excluded services are pre-populated from `billingConfig` in localStorage. |
| **Variants / Markets** | SG, HK, AU, UK |
| **Dependencies / Related Flows** | Subscription Config API (`GET /subscription-config`) — populates excluded-services picker; Billing Config (localStorage `billingConfig.COUPON_DEFAULT_EXCLUDED_SERVICE_CODES`) — pre-populates excluded services on new coupons; Coupon list view (`/coupons`) — navigated to on save/cancel; Invoice billing — coupon applied at billing time; Referral Program flow — `referral_program` coupon type locks `applicableInvoiceType` to `onboardingOnly` |
| **Service / Repository** | sleek-billings-frontend; sleek-billings-api (backend, inferred from `/coupons` API calls) |
| **DB - Collections** | Unknown (frontend only; backend repo not inspected) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which backend service owns the `/coupons` API and what collection does it write to? Are market-specific coupon restrictions enforced on the backend or purely by service-group scoping? Overlap with `clm/coupons/manage-discount-coupons.md` — consider consolidating this form-specific file into that broader capability doc. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/pages/Coupons/CouponForm.jsx` — shared create/edit form; `isEditing` derived from URL param `id`; declarative field-config array drives rendering
- `src/services/api.js:133–158` — `createCoupon` (`POST /coupons`) and `updateCoupon` (`PUT /coupons/:id`)
- `src/services/api.js:142–149` — `getCouponById` (`GET /coupons/:id`) — pre-fills form on edit
- `src/services/api.js:52–55` — `getAllSubscriptionConfig` (`GET /subscription-config`) — populates excluded-services autocomplete
- `src/lib/constants.jsx:300–308` — `COUPON_CALCULATION_TYPE_OPTIONS` (flat, percentage) and `COUPON_APPLICABLE_SERVICE_GROUP_OPTIONS` (General + all subscription type groups)

### Routes
| Path | Component |
|---|---|
| `/coupons/create` | `CouponForm` (create mode) |
| `/coupons/edit/:id` | `CouponForm` (edit mode) |

### Coupon data model (from form fields)
| Field | Values / Notes |
|---|---|
| `code` | String — unique coupon code |
| `title` | Display title |
| `type` | `"coupon"` (default) or `"referral_program"` |
| `calculationType` | `"flat"` or `"percentage"` |
| `amount` | Numeric discount value |
| `maxUsage` | Integer cap on total redemptions; defaults to 1 |
| `expiredAt` | Expiry date, coerced to end-of-day ISO string on submit |
| `applicableServiceGroups` | Multi-select: General, Corporate Secretary, Accounting, Immigration, Mailroom, Business Account, Miscellaneous |
| `excludedServices` | Multi-select of specific service codes from subscription-config catalogue |
| `applicableInvoiceType` | `"allInvoices"` / `"onboardingOnly"` / `"renewalOnly"`; disabled and forced to `"onboardingOnly"` when `type = referral_program` |

### Auth surface
- Bearer JWT (`Authorization: Bearer <token>`) or legacy custom auth token
- `App-Origin: admin` (alternate login) or `admin-sso` — admin-only tool; no customer-facing access
- Base URL from `VITE_API_URL` env var

### Default excluded services behaviour
On create (not edit), the form reads `localStorage.billingConfig.COUPON_DEFAULT_EXCLUDED_SERVICE_CODES` and pre-populates the excluded services field — allowing environment-level defaults without hardcoding.
