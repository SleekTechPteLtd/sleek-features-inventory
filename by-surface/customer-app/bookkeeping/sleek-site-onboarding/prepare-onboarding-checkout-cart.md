# Prepare onboarding checkout cart

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Prepare onboarding checkout cart |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Prospect (website onboarding) |
| **Business Outcome** | Prospects see accurate priced line items and a running total for their selected incorporation or accounting-transfer services and add-ons before checkout, so they can review costs and apply promotions before paying. |
| **Entry Point / Surface** | Sleek marketing website onboarding (incorporation / accounting-transfer paths, including optional add-on pages); API `POST /v2/sleek-site-onboarding/cart-details/` (mounted under `/v2/sleek-site-onboarding` in `app-router.js`). |
| **Short Description** | The backend loads tenant-specific `sleek_site_onboarding` or `sleek_site_onboarding_transfer` app-feature config, resolves Xero item codes from the prospect’s selections (shareholders, accounting plan, ND, immigration quantities, dormant AOT packages, etc.), fetches prices from the Xero catalog via `invoice-vendor-oauth2`, applies quantity and discount logic, optional coupons, and bundle/instant discount lines from onboarding CMS config, then returns a cart payload with `items`, `total`, and `currency`. |
| **Variants / Markets** | Unknown — behaviour is driven by `sleek_site_onboarding` / `subscriptions` / `onboarding` app features and Xero catalog; no explicit SG/HK/AU/UK list in the cited files. |
| **Dependencies / Related Flows** | Xero item catalog (`invoice-vendor-oauth2.getAllItems`, `billing-config-service.getXeroItems`); `invoice-service` (amounts, Xero code resolution, coupon application); `app-features-util` CMS; downstream `POST /v2/invoice/onboarding/:companyId` and related invoice/payment flows for real invoices after account exists; website UI state in `payload.data`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `coupons` (Coupon model — `findOne` by code and expiry for coupon validation); `users` (session user from middleware only when present — for referral/coupon eligibility checks). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `public/api-docs/sleek-site-onboarding.yml` does not document `POST /cart-details/`; confirm whether OpenAPI should be extended. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/sleek-site-onboarding.js`

- **`POST /cart-details/`** — `userService.getUserInfoMiddleWare` (optional auth for coupon/referral context), delegates to `sleekSiteOnboarding.getCartDetails`.

### `controllers-v2/handlers/sleek-site-onboarding/sleek-site-onboarding.js`

- **`getCartDetails`** — Reads `body` and `user` from `req`, calls **`sleekSiteOnboardingService.prepareCheckoutCart(payload, user)`**. On non-success status, returns tenant generic invalid request; on success, JSON `{ status, message, response }` with cart details; logs and returns generic internal error on exceptions.

### `services/sleek-site-onboarding-service.js`

- **`prepareCheckoutCart`** — **`validatePayload`** requires `payload.data`. Loads feature via **`appFeatureUtil.getAppFeaturesByName`** using **`namingWithValidateAccountingTransfer("sleek_site_onboarding", payload)`** (switch to `*_transfer` when `data.isAccountingTransfer`). **`filterOutBusinessAccountSubscription`**, **`getItemsFromPayloadSelectedServices`** (main subscription walk, dormant AOT branch via **`invoiceVendor.getAllItems`**, **`addAmountAddOnServiceFromPayload`**), **`invoiceService.getAmountChargedFromItems`**, **`applyCoupon`** (Coupon `findOne`, **`invoiceService.applyCompanyCoupon`** for general coupons), **`getCheckoutItems`** + **`addInstantDiscountToCheckoutList`** ( **`appFeatureUtil.getAppFeaturesByName("onboarding", "customer")`**, **`billingConfigService.getXeroItems("main")`**, **`pushAdditionalDiscounts`**). Returns `{ status, response: { items, total, currency } }`.
- **`ONBOARDING_FLOW`** — Incorporation vs transfer via **`data.onboardingFlow`** (`incorp` / `transfer`).
- **`isServicePurchased`** / **`getCheckoutItems`** — Map payload selections (mailroom, shareholders, accounting, ND, immigration, business account, add-on packages, audit/tax, GST, etc.) to purchased flags and line totals.

### Related modules (not in FEATURE_LINE but referenced)

- `vendors/invoice-vendor-oauth2`, `services/invoice-service.js`, `services/billing-config-service.js`, `utils/app-features-util.js`, `schemas/coupon.js`.

### Columns marked Unknown

- **Variants / Markets**: Tenant and CMS feature flags define catalog and flows; no fixed country enumeration in the cited files.
