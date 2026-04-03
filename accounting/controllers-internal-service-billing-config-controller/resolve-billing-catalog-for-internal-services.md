# Resolve billing catalog for internal services

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Resolve billing catalog for internal services |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Trusted internal callers obtain a single, normalized view of subscription and invoicing line items (Xero-linked or subscription-microservice–backed) per client type so integrations and downstream services align with the platform billing catalog. |
| **Entry Point / Surface** | Internal HTTP API on sleek-back: `GET /internal/admin/billing-config/:clientType`. Guard: `internalServicesMiddleware()` — Basic auth using the configured internal-service secret (`Authorization: Basic …` with `clientId:clientSecret` base64); optional bypass in non-production via internal-service config. Not intended for browser or public clients. |
| **Short Description** | Returns JSON describing billing line items for the given `clientType`: either mapped rows from the subscription microservice when the `billing_service` app feature enables `use_service_microservice`, or Xero items merged with `BillingConfig` overrides from MongoDB. Ordering prefers configured rows; responses are gated by tenant billing config, `bypass_xero`, and feature flags. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Xero**: `invoice-vendor-oauth2` `getAllItems(clientType)` when not using the microservice path. **Sleek subscription**: `modules/sleek-subscription/services/service.service` `getServices(clientType)` when `billing_service.sleek_back.use_service_microservice` is enabled. **App features**: `bypass_xero` (admin), `billing_service` / `use_service_microservice` (general). **Tenant**: `tenant.features.admin.companies.billing.config.enabled`. **Shared config**: `xeroInvoiceCodes` for default service keys when mapping Xero items. Related: `getXeroItems` is also used by `getXeroCodesAndItems`, `updateXeroItems`, and subscription-date logic elsewhere in the same service. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `billingconfigs` (read via `BillingConfig.find({ client_type })` on the Xero + local config path; bulk writes use `BillingConfig.collection` in `updateXeroItems`, which this controller does not call). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which internal services call this route is not enumerated in these files. Market-specific behaviour beyond `bypass_xero` and tenant flags is configuration-dependent. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/internal-service/billing-config-controller.js`

- **`GET /internal/admin/billing-config/:clientType`** — `internalServicesMiddleware()` then `billingConfigService.getXeroItems(clientType)`.
- If the service returns a falsy value (`false` when bypass or tenant billing config is off), handler throws `Not found xero items` and responds with generic internal server error payload.
- Success: `200` with the object returned by `getXeroItems` (typically `{ xeroItems: [...] }`, sometimes with a message when empty).

### `middlewares/internal-services.js`

- **`internalServicesMiddleware`** — Validates Basic credentials against `internalService.getSecretToken()`; sets `req.clientId`; `401` without token, `403` on secret mismatch; optional bypass path for internal testing.

### `services/billing-config-service.js`

- **`getXeroItems(clientTypeConfigName, activeOnly)`** — Short-circuits to `false` if `bypass_xero` (admin app feature) is enabled, or if `tenant.features.admin.companies.billing.config.enabled` is false.
- **Microservice branch**: When `billing_service` / `sleek_back` / `use_service_microservice` is enabled, loads `subscriptionService.getServices(clientTypeConfigName)` and maps fields to the legacy-shaped payload (`xero_id`, `xero_code`, `service`, `unit_price`, `account_code`, display flags, `billing_cycle`, `recurring`, etc.).
- **Xero branch**: `invoiceVendor.getAllItems(clientTypeConfigName)`; `BillingConfig.find({ client_type: clientTypeConfigName })`; merges each Xero item with optional `BillingConfig` row and `xeroInvoiceCodes` defaults.
- **`activeOnly`**: When true, filters to `xero_status === 'active'` before sorting (not used by this controller, which calls with one argument).
- Returns `{ xeroItems: orderBy(...), message? }` or `{ xeroItems: [] }` with error message when no services.

### `schemas/billing-config.js`

- **Mongoose model `BillingConfig`** — Fields include `xero_code`, `service_ref`, `client_type` (`main` \| `manage_service`), `duration`, `billing_cycle`, `service_type`, `xero_status`, `recurring`, `disbursement`, `display_in_admin`, `display_in_customer`, `update_by` (User ref). Supports merge with Xero API rows in `getXeroItems`.
