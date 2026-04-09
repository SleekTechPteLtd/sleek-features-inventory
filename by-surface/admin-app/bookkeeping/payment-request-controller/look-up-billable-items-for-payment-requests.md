# Look up billable items for payment requests

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Look up billable items for payment requests |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Admins can see which services and Xero catalog lines are valid when building a payment request so charges match billing rules and permissions. |
| **Entry Point / Surface** | Sleek Admin — authenticated admin APIs used while composing payment requests (`GET /admin/payment-requests/item-names/:serviceType`, `GET /admin/payment-requests/xero-items`; exact UI path not determined in backend). |
| **Short Description** | Returns billable line options in two ways: (1) static Xero service definitions filtered by service type, gated by app-feature `allowed_service_types`; (2) live Xero / billing-config catalog items for payment requests, gated by full `invoices` permission, excluding configured credit-balance codes. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | App features (`payment_request`, `bypass_xero`, `billing_service`); `billing-config-service` and optional subscription microservice; Xero via `invoice-vendor-oauth2`; shared-data flags (`xeroCodesHiddenInPaymentRequest`, `xeroCodesWithMandatorySubDate`, `xeroCreditBalanceCodes`); creating/sending payment requests (`POST /admin/payment-requests`). |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `groups` (permission resolution for Xero items); `billingconfigs` when billing config path is used; app feature data may be loaded via app-feature service (not necessarily Mongo in this repo). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Routes and guards (`controllers/admin/payment-request-controller.js`)

- **`GET /admin/payment-requests/item-names/:serviceType`** — `userService.authMiddleware`. Loads `payment_request` admin app feature; `allowed_service_types` must include `req.params.serviceType` or `INVALID_SERVICE_TYPE`. Response: subset of `constants/xero-services.js` where `serviceType` matches (item metadata: codes, names, prices, `hasSubscriptionDate`, `hasQuantity`).
- **`GET /admin/payment-requests/xero-items`** — `userService.authMiddleware`, then `accessControlService.userHasPermission(req.user, "invoices", "full")` or 401. Calls `paymentRequestService.getPaymentRequestXeroItems(req.clientTypeConfigName)`; filters out item codes in `xeroCreditBalanceCodes` from shared-data; empty list returns `EMPTY_XERO_LIST`.

### Catalog assembly (`services/payment-request-service.js`)

- **`getPaymentRequestXeroItems(clientTypeConfigName)`** — Prefers `billingConfigService.getXeroItems(clientTypeConfigName)` and maps active rows, omitting codes in `xeroCodesHiddenInPaymentRequest`, enriching with `isSubDateMandatory`, `isDiscountItem`, `duration`, `service`, `recurring`. If no config, **`getXeroItemsUsingConfigFile`** uses `invoiceVendor.getAllItems(clientTypeConfigName)` and applies the same hide / mandatory-sub-date rules from shared-data.

### Static service-type catalog (`constants/xero-services.js`)

- Exported array of Xero-style line definitions keyed by `serviceType` (e.g. `accounting`, `corpSec`, `nomineeDirector`, `mailroom`, `discount`) with `itemCode`, pricing, and flags — used by `item-names` after service-type allowlisting.

### Permissions (`services/access-control-service.js`)

- **`userHasPermission(user, resourceName, accessType)`** — Resolves group roles (and parent groups) against role permissions; used for `invoices` / `full` on the Xero items endpoint.
