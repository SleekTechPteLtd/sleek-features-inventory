# Browse pricing and invoice history

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Browse pricing and invoice history |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User (company user with billing access) |
| **Business Outcome** | Customers see which services are billable, what their current charges would be, and a complete picture of company invoices—including amounts in progress—so they can plan payment and reconcile billing. |
| **Entry Point / Surface** | Sleek customer app — authenticated APIs under company billing (`GET /payment/items`, `GET /companies/:companyId/charge-amount`, `GET /companies/:companyId/invoices`, `GET /companies/:companyId/paginated-invoices`; exact navigation labels not determined in backend). |
| **Short Description** | Exposes the active billable catalog (Xero items or billing-config / subscription service mirror), computes quoted line amounts and totals for the company’s subscriptions with optional coupon handling, and lists internal invoice records (full or paginated). In-flight payments are represented as invoices with `status: "processing"` and a `tag` set during payment flows; list endpoints return all invoices for the company for client-side filtering. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `billing-config-service` (`getXeroItems`, optional subscription microservice via `billing_service` app feature); `invoice-vendor-oauth2` (`getAllItems`, Redis-cached Xero catalog); company subscriptions and coupons; payment flows that create/update `processing` invoices with `invoice_tag` (`POST /payment/company-subscriptions`, etc.); external Xero invoice creation elsewhere in `invoice-service`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `invoices` (Invoice model); `billingconfigs` when billing config path is used; Xero settings/tokens via existing Xero integration (not necessarily extra collections for read paths beyond cache). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | List routes do not accept `status` or `tag` query parameters—filtering for “processing” or by tag is assumed to happen in the client using returned invoice fields (`invoice.js` schema). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Catalog — billable items (`controllers/payment-controller.js`)

- **`GET /payment/items`** — `userService.authMiddleware`. Query: `is_transfer` (boolean, required). Loads `billingConfigService.getXeroItems(req.clientTypeConfigName)`, keeps `xero_status === 'active'`, returns `invoiceService.getAvailableItemsFromBillingConfig(allItems, isTransfer)`; if no config, `invoiceVendor.getAllItems(req.clientTypeConfigName)` and `getAvailableItems`. Maps to JSON with `code`, `description`, `price`, `service`, `duration`, `serviceClassification`, `recurringPeriod` (`invoice-service.js`: `getAvailableItemsFromBillingConfig`, `convertConfigXeroItemsToJson`, `convertXeroItemsToJson`).

### Quoted charge amounts (`controllers/payment-controller.js`)

- **`GET /companies/:companyId/charge-amount`** — `userService.authMiddleware`, `companyService.canManageCompanyMiddleware("companyUser")`. Optional query `xeroSubcriptionOnly`. Resolves coupon via `invoiceService.getCompanyCoupon`, loads company line items via `getItemsFromCompany`, then `getAmountChargedFromItems` and `applyCompanyCoupon`. Response: structured amounts per line and totals.

### Invoice lists (`controllers/payment-controller.js`)

- **`GET /companies/:companyId/invoices`** — same guards. `Invoice.find({ company }).sort({ _id: "desc" })` — returns full array.
- **`GET /companies/:companyId/paginated-invoices`** — same guards; validates `skip`; `limit` from `sharedData.invoices.limitPerSearch`; returns `{ invoices, count }` with `where("number").ne(null)`.

### Processing invoices — status and tag (`controllers/payment-controller.js`, `schemas/invoice.js`)

- Internal invoices use `status` (enum from `sharedData.invoices.status`) and `tag` (string). Payment routes build or match `{ company, status: "processing", tag: req.body.invoice_tag, ... }` when `invoice_tag` is present (e.g. company subscription card payment). Clients listing `/companies/:companyId/invoices` can filter to processing rows and by `tag` in memory.

### Billing config vs Xero (`services/billing-config-service.js`)

- **`getXeroItems`** — App features `bypass_xero`, tenant billing config, optional `billing_service.sleek_back.use_service_microservice` → subscription service `getServices`; else `invoiceVendor.getAllItems` merged with `BillingConfig.find({ client_type })`. **`updateXeroItems`** upserts `BillingConfig` collection.

### Xero OAuth and items (`vendors/invoice-vendor-oauth2.js`)

- **`getAllItems(configName)`** — Redis cache key `getAllItems-${configName}`; on miss, `getXeroClientToken` → `xero.accountingApi.getItems(tenantId)`.

### Amount and catalog helpers (`services/invoice-service.js`)

- **`getItemsFromCompany`**, **`getAmountChargedFromItems`** (per-line `amount`, `price`, `description`, `code`, discounts, `totalAmount`), **`getAvailableItemsFromBillingConfig`**, **`applyCompanyCoupon`**, **`getCompanyCoupon`**.
