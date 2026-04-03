# Manage company subscriptions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage company subscriptions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations user (authenticated admin with `companies` full access) |
| **Business Outcome** | Internal staff can see subscription coverage and billing-related state across companies, correct statuses and dates, and attach paid services to a company so billing records and entitlements stay aligned. |
| **Entry Point / Surface** | Authenticated admin HTTP API: `GET /api/get-all-company-subscriptions`, `GET /companies/:companyID/subscriptions`, `PUT /company-subscriptions/:companySubscriptionId/change-status`, `POST /companies/:companyId/insert-subscription-to-company` (all under `userService.authMiddleware` and `accessControlService.can("companies", "full")`). The same list-all handler is also mounted at `GET /admin/company-subscriptions` via `controllers/admin/company-subscription-controller.js`. Exact product UI labels are not defined in these files. |
| **Short Description** | **List all**: filterable aggregation over companies and embedded subscriptions with pagination, optional unlimited result set (noted for renewal automation), joins to invoices and external payment info, and owner user on each row. **Per company**: returns subscriptions from the sleek-subscription microservice when `microservice_enabled`, otherwise enriches embedded `company.subscriptions` with billing config / Xero item metadata and feature-flagged visibility rules. **Status**: updates one or many active subscriptions to a validated status, clears cancellation fields, optionally turns off auto-renew on churn/discontinue, and writes auditor logs. **Attach subscription**: validates Xero item code, activation/expiry, and invoice number; resolves service from billing config or legacy Xero map; inserts or updates nested subscription and service lines on the company document, with audit logging. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Sleek subscription service**: `getSubscriptionList` when company has `microservice_enabled`. **Billing**: `billing-config-service` (`getXeroItems`), tenant `xeroInvoiceCodes`, `tenant.features.admin` flags (`revamped_company_subscriptions`, `activate_service`, `uniqueServiceNames`, billing config). **Persistence**: `company-subscriptions-schema-service` for embedded subscription CRUD. **History**: `company-subscription-service.insertManualSubscriptionHistory` from related PUT handlers in the same module (mounted on legacy `controllers/admin/company-subscription-controller.js` routes). **Audit**: `auditorService.saveAuditLog` with `buildAuditLog`. **Downstream**: comment in list-all references `sleek-renewal-service` for `limitDisabled` queries. **Related (not in this file set)**: `company-subscription-controller.js` adds single-subscription GET, cancellation updates, move-to-paid, reminders, activate/deactivate, and other PUTs that delegate to `put-company-subscriptions.js`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies` (embedded `subscriptions` and `subscriptions.services`; `loadSubscriptions` on insert path); `companyusers` (owner lookup and resource-role filters in list-all); `invoices` (lookup and validation by number); `externalpaymentinfos` (aggregation lookups); `companyresourceusers`, `resourceallocationroles`, `users` (optional list-all filters for CSS/accounting owner); manual subscription history rows when `company-subscription-service.insertManualSubscriptionHistory` is invoked from sibling PUT handlers. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether all operations teams use v2 paths (`/api/...`, `/companies/...`) vs legacy `/admin/company-subscriptions/...` for overlapping behaviour; confirm UI mapping for microservice vs legacy subscription payloads. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/admin.js`

- **`GET /api/get-all-company-subscriptions`** → `getAllCompanySubscriptions` (`can("companies", "full")`).
- **`GET /companies/:companyID/subscriptions`** → `getCompanySubscriptions`.
- **`PUT /company-subscriptions/:companySubscriptionId/change-status`** → `putCompanySubscriptionChangeStatus` only (other `putCompanySubscriptionChange*` exports are registered from `controllers/admin/company-subscription-controller.js`).
- **`POST /companies/:companyId/insert-subscription-to-company`** → `insertSubscriptionToCompany` (`can("companies", "full")`).

### `controllers-v2/handlers/admin/all-company-subscriptions.js`

- **`getAllCompanySubscriptions`**: Validates query filters (`service`, `duration`, `is_auto`, overdue and cancellation date ranges, `cancellation_status`, `company`, `is_cancelling`, secondary filters for payment/company status, CSS/accounting assignees, subscription status); builds `Company.aggregate` pipeline: `$unwind` subscriptions, match paid/unpaid shape, sort (company, service, status, duration, overdue, etc.), `$lookup` `externalpaymentinfos` and `invoices`, optional extra lookups for resource roles when filtering by assignee; `$facet` for total count + skip/limit unless `limitDisabled` (renewal-service use case); maps each row to a flat subscription object with nested `company` and populated `owner` via `CompanyUser` + `userService.sanitizeUserData`.

### `controllers-v2/handlers/admin/get-company-subscriptions.js`

- **`getCompanySubscriptions`**: Loads `Company` by `req.params.companyID`. If `microservice_enabled`, returns `getSubscriptionList({ companyId, status })` from `modules/sleek-subscription/services/subscription.service` with optional non-active services per `tenant.features.admin.revamped_company_subscriptions`. Else filters/maps embedded `companyDetails.subscriptions` using `BillingConfig`, `billingConfigService.getXeroItems`, `xeroInvoiceCodes`, inactive handling, and `activate_service` / display flags.

### `controllers-v2/handlers/admin/put-company-subscriptions.js`

- **`putCompanySubscriptionChangeStatus`**: Validates `status` (`SUBSCRIPTION_STATUSES_ENUM`), optional `update_all_active_subscriptions`. Loads subscription via `companySubscriptionsSchemaService.getSubscriptionById`; may batch-update all subscriptions matching allowed statuses via `getSubscriptionsByCompanyId`, `updateSubscription`, `unsetSubscriptionData` (cancellation fields); sets `is_auto` false for churn/discontinue when not batching. Persists auditor log `subscriptions-update` comparing company before/after.
- **Same module (used by legacy admin router, not `controllers-v2/admin.js`)**: `putCompanySubscriptionChangeExpiry`, `putCompanySubscriptionChangeActivationDate`, `putCompanySubscriptionChangeInfo` (bulk field updates + `insertManualSubscriptionHistory`), `putCompanySubscriptionChangeAutoRenewal`.

### `controllers-v2/handlers/company/insert-subscription-handler.js`

- **`insertSubscriptionToCompany`**: Optional `?isMultiple=true` with array body; else single body. Loads company, `loadSubscriptions()`, validates payload (`itemCode`, `activationDate`, `expiryDate`, `invoiceNumber`). Resolves catalog item via `billingConfigService.getXeroItems` when `features.admin.companies.billing.config.enabled`, else `invoiceService.getSelectedServiceFromXeroCode`. Validates invoice belongs to company. Optional duplicate-active guard when `uniqueServiceNames` enabled. Either updates existing subscription (extend `overdue_at`, reactivate inactive, `insertServiceToSubscription`) or `insertToSubscription` with new subdocument id. Audit log type `insert-to-company-subscriptions`.
