# Manage company subscription services

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage company subscription services |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (admin API with `company_services` permission) |
| **Business Outcome** | Keep per-invoice subscription line items accurate so billing periods, service types, and invoice links stay aligned with what the company is sold and charged for. |
| **Entry Point / Surface** | Authenticated admin HTTP API on sleek-back: `GET /admin/company-services/:companyServiceId`, `PUT /admin/company-services/:companyServiceId`, `PUT /admin/company-services/:companyServiceId/edit-and-refresh-subscription`, `DELETE /admin/company-services/:companyServiceId` (`company_services` read for GET; `full` for mutating routes). Exact Sleek admin UI label for these routes is not defined in the referenced files. |
| **Short Description** | Operations staff load a single nested company service (start/end, duration, type, linked invoice) by id; update timing, duration, service type, and/or invoice reference with validation and recomputed `end_at`; optionally run an “edit and refresh subscription” path that reactivates subscription status from app-feature constants, may assign a nominee director for director-related services, extends company-level subscription windows and company fields (e.g. service-specific end dates via `sharedData.services.companyEndAt`), and writes subscription history. They can also remove a service line from the subscription. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Invoices**: `Invoice.findById` on PUT when `invoice` is sent; invoice lookups in `getServiceById` aggregation. **Company subscription roll-up**: `companySubscriptionService.resolveFinalCompanyStatusDuringPayment`, `insertSubscriptionHistory` (Xero manual invoice transaction type). **Nominee director**: `companyUserService.getNomineeDirector`, `assignNomineeDirector` with `ND_ENTRY_POINTS.RECONCILE` when service type relates to director. **Config / app features**: `appFeatureUtil.getAppFeaturesByName("MAPS_CONSTANTS", "general")` for `SUBSCRIPTION_STATUSES`; `sharedData.services.types` and `sharedData.services.companyEndAt` for service typing and company field keys. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies` (nested `subscriptions` and `subscriptions.services` updated via `updateOne` / `$pull`); `invoices` (read for existence checks and populated invoice on fetch). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Confirm which admin product surface calls `edit-and-refresh-subscription` versus plain PUT. Whether microservice-enabled companies are excluded from this controller path or handled elsewhere is not shown in these two files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/admin/company-service-controller.js`

- **`GET /admin/company-services/:companyServiceId`** — `userService.authMiddleware`, `accessControlService.can("company_services", "read")`; `companySubscriptionsSchemaService.getServiceById`; 422 if missing.
- **`PUT /admin/company-services/:companyServiceId`** — `can("company_services", "full")`; `validationUtils.validateOrReject` for `start_at` (date), `duration` (number), `service` (string in `sharedData.services.types`), `invoice` (string), strict; verifies invoice exists when provided; builds `data` with `end_at` = `moment(start_at).add(duration, "months")`; `updateService(companyService._id, subscription, company._id, data)`.
- **`PUT /admin/company-services/:companyServiceId/edit-and-refresh-subscription`** — `can("company_services", "full")`; requires `start_at`; merges invoice from body or existing; sets `status` to active from `SUBSCRIPTION_STATUSES`; `updateService`; for director-related services may assign nominee director via `companyUserService`; computes `potentialEndOfService` / `newOverdueAt` against existing company subscriptions; when conditions on `overdue_at` vs `potentialEndOfService` hold, runs `updateSubscription` and `Company.updateOne` with `companySubscriptionService.resolveFinalCompanyStatusDuringPayment` and `sharedData.services.companyEndAt[companyService.service]`; `insertSubscriptionHistory` with `config.subscriptionPaymentType.xeroInvoice` and `config.subscriptionTransactionType.manualXeroInvoice`.
- **`DELETE /admin/company-services/:companyServiceId`** — `can("company_services", "full")`; `deleteService(service._id, subscription, company._id)`.

### `services/subscriptions/company-subscriptions-schema-service.js`

- **`getServiceById(serviceId)`** — `Company.aggregate`: match `subscriptions.services._id`, unwind subscription/services, `$lookup` `invoices` on `subscriptions.services.invoice`; projects service fields plus `company` root and `subscription` id.
- **`updateService(serviceId, subscriptionId, companyId, data)`** — `processServiceData` → positional keys `subscriptions.$[outer].services.$[inner].*`; `Company.updateOne` with `arrayFilters` for outer subscription and inner service ids.
- **`updateSubscription(subscriptionId, companyId, data)`** — `processSubscriptionData` → `subscriptions.$.<field>`; used by edit-and-refresh path.
- **`deleteService(serviceId, subscriptionId, companyId)`** — `$pull` `subscriptions.$.services` by service `_id`.

### Related schema shape (inferred)

- Services are embedded under `company.subscriptions[].services[]` with fields including `_id`, `service`, `duration`, `start_at`, `end_at`, `invoice`, timestamps.
