# Renew subscription after manual payment

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Renew subscription after manual payment |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations staff (authenticated admin with company-services full access) |
| **Business Outcome** | After a subscription is paid outside the self-serve flow, operations can align the company’s subscription period, company status, service end dates, nominee director assignment, and audit history so entitlements match what was collected. |
| **Entry Point / Surface** | Authenticated admin HTTP API: `PUT /admin/company-services/:companyServiceId/edit-and-refresh-subscription` (`userService.authMiddleware`, `accessControlService.can("company_services", "full")`). Exact admin UI screen label is not defined in these files. |
| **Short Description** | Staff submit a paid-period start (`start_at`, optional `duration`). The route reloads the company service, sets the service slice to active with computed `end_at`, updates the nested subscription on the company (including `overdue_at` extension from prior periods or “similar” subscriptions for director/mailroom/accounting/corp-sec families), and may set company `status` (e.g. churned → live when paying) plus the service-specific company end-date field from `sharedData.services.companyEndAt`. For director-related services, if no nominee director exists on the company, it resolves one via `getNomineeDirector` and `assignNomineeDirector` with entry point reconcile. Finally it logs a manual Xero invoice subscription history row when the subscription-history feature flag is enabled. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **App features**: `MAPS_CONSTANTS` (`SUBSCRIPTION_STATUSES`, `COMPANY_STATUSES`) from general CMS; optional `updated_assigning_nd_process` for ND selection. **Billing**: `billingConfigService.getXeroCodesAndItems` inside `insertSubscriptionHistory` for line mapping. **Related**: simpler `PUT /admin/company-services/:companyServiceId` updates service dates/invoice without the full refresh, ND assignment, company status merge, or subscription history. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies` (embedded `subscriptions` and `subscriptions.services`; top-level `status` and per-service end fields per `sharedData.services.companyEndAt`); `companyusers` (read for existing ND; create when assigning ND); `companysubscriptionhistories` (via `CompanySubscriptionHistory.create` when feature enabled); `invoices` (populated on service for history and lookups in schema service aggregates). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Confirm which admin UI action maps to `edit-and-refresh-subscription` vs the lighter `PUT` on the same resource. History rows depend on `features.admin.companies.billing.subscriptionHistory.enabled` and a resolvable invoice/line mapping—document edge cases when `items` is undefined and invoice lacks line items. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/admin/company-service-controller.js`

- **`PUT /admin/company-services/:companyServiceId/edit-and-refresh-subscription`** — validates `start_at` (required), optional `duration` (strict). Loads service via `companySubscriptionsSchemaService.getServiceById`. Builds `data` with `start_at`, `duration`, `service`, `invoice` (body or existing); sets `end_at` from `start_at + duration`, `status` to `SUBSCRIPTION_STATUSES.ACTIVE`; calls `updateService(...)`.
- **Post-update**: reloads `Company` by id. **Nominee director**: if `bodyCleaned.service` or `companyService.service` contains `"director"`, queries `CompanyUser` for existing nominee; if none, `companyUserService.getNomineeDirector(updatedCompany._id)` then `assignNomineeDirector(updatedCompany._id, ndToAssign, { entrypoint: ND_ENTRY_POINTS.RECONCILE })`.
- **Subscription extension math**: finds matching or “similar” subscription on `updatedCompany.subscriptions` (same service/duration, or director/mailroom/accounting/corp-sec family) to anchor `existingSubOverdueAt`; computes `potentialEndOfService` and `newOverdueAt` from `start_at`/`duration` or stacked on prior `overdue_at`.
- **Conditional parent subscription + company document update**: only if `companyService.overdue_at` is null or before `potentialEndOfService` — `companySubscriptionService.resolveFinalCompanyStatusDuringPayment(companyCompleteDetails, [companySubscriptionToUpdate])` for `status`, and `$set` of `[sharedData.services.companyEndAt[companyService.service]]: potentialEndOfService`; parallel `companySubscriptionsSchemaService.updateSubscription` with `active_at`, `overdue_at`, `duration`, `status` ACTIVE, `last_reminded_at` cleared.
- **History**: `companySubscriptionService.insertSubscriptionHistory(req.user, updatedCompany, undefined, get(companyService, "invoice"), config.subscriptionPaymentType.xeroInvoice, config.subscriptionTransactionType.manualXeroInvoice)` then `res.json({ message: "success" })`.

- **`PUT /admin/company-services/:companyServiceId`** (related, lighter path) — validates `start_at`, `duration`, `service`, `invoice`; optional invoice existence check; computes `end_at`; `updateService` only (no ND, no company-level subscription refresh, no `insertSubscriptionHistory` in this handler).

- **`GET /admin/company-services/:companyServiceId`** — `can("company_services", "read")`; returns service or 422.

- **`DELETE /admin/company-services/:companyServiceId`** — `deleteService`.

### `services/subscriptions/company-subscriptions-schema-service.js`

- **`getServiceById`**: `Company.aggregate` matching `subscriptions.services._id`, `$lookup` invoices; returns service row with `company`, `subscription` id.
- **`updateService`**: `Company.updateOne` with array filters on `subscriptions.$[outer].services.$[inner]` fields.
- **`updateSubscription`**: `Company.updateOne` with `subscriptions.$` positional updates for subscription-level fields.

### `services/company-subscription-service.js`

- **`resolveFinalCompanyStatusDuringPayment`**: if company `status` is churn and there are subscriptions being paid, returns `COMPANY_STATUSES.LIVE`; else retains current status.
- **`insertSubscriptionHistory`**: gated by `tenant.features.admin.companies.billing.subscriptionHistory.enabled`; uses `billingConfigService.getXeroCodesAndItems`, iterates invoice line items (or `items` argument), `CompanySubscriptionHistory.create` with payment type and transaction type passed from caller (`manualXeroInvoice` / `xeroInvoice` for this flow).

### `services/company-user-service.js`

- **`getNomineeDirector(companyId)`**: resolves default or feature-flagged V2 pool (`getNomineeDirectorV2`) to pick a `User` with `is_nominee_director`.
- **`assignNomineeDirector(company, user, options)`**: creates `CompanyUser` with director flags, increments ND assignment counts via `nomineeDirectorService`, may trigger incorporation side effects (`autoTriggersNameReservationFiling`).
