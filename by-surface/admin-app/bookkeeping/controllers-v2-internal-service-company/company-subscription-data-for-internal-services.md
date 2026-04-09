# Company subscription data for internal services

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Company subscription data for internal services |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Trusted internal callers can resolve a company’s subscription lines and billing display context in one call so orchestration jobs, admin tooling, and support flows stay aligned with active services and how they should appear. |
| **Entry Point / Surface** | Internal HTTP API on sleek-back: `GET /companies/:companyID/subscriptions` (mounted on the internal-services router). Guard: `internalServicesMiddleware()` — Basic auth with shared secret (`Authorization: Basic …`); optional bypass via internal-service config. Not intended for browser or public clients. |
| **Short Description** | For microservice-enabled companies, loads subscriptions via `getSubscriptionList` (Sleek Billings when enabled, otherwise sleek-subscription HTTP API with optional status filter from tenant `revamped_company_subscriptions`). For legacy companies, reads embedded `company.subscriptions`, optionally filters inactive lines using tenant constants and billing config, and enriches each line with Xero/billing-config metadata (`serviceType`, `display_in_admin`, `display_in_customer`, `hideAutoRenewal`). Returns JSON `{ companySubscriptions, count }`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Sleek subscription microservice** (`config.sleekSubscription.baseUrl`). **Sleek Billings** (`sleekBillingsService.getSleekBillingsConfig`, `getSubscriptionsByCompanyId`) when `SWITCH_TO_SLEEK_BILLINGS === "enabled"`. **Billing config**: `billingConfigService.getXeroItems`, `BillingConfig` schema, `config/shared-data` `xeroInvoiceCodes`, `tenant.features.admin.revamped_company_subscriptions`, `tenant.features.admin.companies.billing.activate_service.enabled`, `tenant.general.MAPS_CONSTANTS.SUBSCRIPTION_STATUSES`. **Related**: admin `getCompanySubscriptions` handler reused by internal route. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies` (read `microservice_enabled`, `subscriptions`, `partner`); `billing_configs` (read by `client_type` for legacy enrichment). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | If `microservice_enabled` is false and `company.subscriptions` is missing/empty, the handler may not send a response before falling off the function (verify runtime behaviour). Exact internal callers (service names) are not named in these files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/internal-service/company.js`

- **`GET /companies/:companyID/subscriptions`** — `internalServicesMiddleware()`, handler `getCompanySubscriptions` from `../handlers/admin/get-company-subscriptions`.

### `controllers-v2/handlers/admin/get-company-subscriptions.js`

- **`getCompanySubscriptions`** — `Company.findOne({ _id: req.params.companyID })`; 404-style error via `ERROR_CODES.COMPANY` if missing.
- **Microservice path** (`companyDetails.microservice_enabled`) — `getSubscriptionList({ companyId, status })` where `status` is `'active'` or `null` depending on `tenant.features.admin.revamped_company_subscriptions.show_non_active_services`; response `200` with `companySubscriptions`, `count`.
- **Legacy path** — Uses `companyDetails.subscriptions`; optional filter by inactive status and `activate_service` feature; maps subscriptions with `BillingConfig.find({ client_type })` (`partner` → `manage_service`, else `main`), `billingConfigService.getXeroItems`, `xeroInvoiceCodes` lookup for `service`/`duration` → `xeroCode`, merge with `configSettings` / `xeroItems` for `serviceType`, `display_in_admin`, `display_in_customer`; `hideAutoRenewal` for dormant plan inclusions; spreads `sub.toObject()` into response objects.

### `modules/sleek-subscription/services/subscription.service.js`

- **`getSubscriptionList({ companyId, services, status })`** — When Sleek Billings switch is on, `sleekBillingsService.getSubscriptionsByCompanyId(companyId)` and `mapSubscriptionFromSleekBillings`; else `http_request.getResource` to `${config.sleekSubscription.baseUrl}/subscriptions?companyId=…&load=service` with optional `status` / `service` query params; maps via `mapSubscription` (fields include `_id`, `name`, `service`, `duration`, `quantity`, `is_auto`, dates, `status`, `recurring`, `isFinancialYear`, `serviceType`, `code`, `tier`, `companyId`).
