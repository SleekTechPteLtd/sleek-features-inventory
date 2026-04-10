# Manage Customer Subscriptions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Customer Subscriptions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (internal Sleek billing staff / Billing Admin) |
| **Business Outcome** | Gives billing operators full control over the subscription lifecycle — searching, reviewing, updating renewal terms, tracking service delivery progress, offboarding, and cancelling — to keep billing accurate and services running for each customer. |
| **Entry Point / Surface** | Internal billing admin API (`sleek-billings-backend`) — consumed by Sleek Ops portal or equivalent internal tooling via REST |
| **Short Description** | Operators can search and filter customer subscriptions, modify renewal amounts and dates, toggle or cancel auto-renewal, update financial year-end, mark deliverables as complete, offboard or reactivate subscriptions, and hard-delete records. Bulk field patching via CSV is available to BillingSuperAdmin users. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Invoice module (subscription creation from invoice); Subscriptions Config / Service Catalog; Company profile (FYE, incorporation date); Audit Logs (every mutation is logged); Service Delivery API (task status sync on reactivate/discontinue); FYE Update pipeline (`fye-update.service`); Auto-renewal scheduler (`subscription-auto-renewal.service`, `customer-subscription-scheduler.service`) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `customersubscriptions`, `servicedeliveries`, `invoices` (lookup), `services` (lookup) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | (1) `GET /update-auto-renewal-toggle-off` is an HTTP endpoint that fires a scheduler action — is it called manually or also by a cron job? (2) Master authorization key path in `cancelRenewal` — which internal system uses this key? (3) Which UI calls the `mass-patch-data` CSV upload endpoint? (4) Are all four markets (SG/HK/UK/AU) served from the same deployed instance? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `customer-subscription/controllers/customer-subscription.controller.ts`

| Method | Route | Auth | Purpose |
|---|---|---|---|
| GET | `/customer-subscriptions` | `@Auth()` | List/filter subscriptions by company, status, service type |
| GET | `/customer-subscriptions/search` | `@Auth()` | Paginated aggregate search with sorting |
| GET | `/customer-subscriptions/search/accounting-upgrades` | `@Auth()` | Search accounting upgrade subscriptions |
| PUT | `/customer-subscriptions/update-service-delivery-status` | `@Auth()` | Mark individual deliverables delivered or reopen them |
| POST | `/customer-subscriptions/trigger-fye-updates` | `@Auth()` | Batch-trigger financial year-end updates |
| PUT | `/:id/custom-renewal-amount` | `@Auth()` | Override renewal amount with reason |
| PUT | `/:id/next-renewal-date` | `@Auth()` | Adjust next renewal date; auto-sets renewal status |
| PUT | `/:id/financial-year-end` | `@Auth()` | Update service FYE year |
| PUT | `/:id/toggle-renewal` | `@Auth()` | Enable or disable auto-renewal |
| PUT | `/:id/cancel-renewal` | `@Auth()` | Cancel renewal; supports master-auth-key bypass for system calls |
| PUT | `/:id/reactivate` | `@Auth()` | Reactivate an offboarded subscription |
| PUT | `/:id/offboard` | `@Auth()` | Mark subscription as `toOffboard` |
| PUT | `/:id/patch-data` | `@Auth()` + `@GroupAuth(BillingSuperAdmin)` | Arbitrary field patch for admins |
| POST | `/mass-patch-data` | `@Auth()` + `@GroupAuth(BillingSuperAdmin)` | Bulk field patch via CSV file upload |
| PUT | `/:id/discontinue` | `@Auth()` | Discontinue a subscription |
| DELETE | `/:id` | `@Auth()` | Hard-delete a subscription record |
| GET | `/suggested-subscriptions` | `@Auth()` | Suggest subscriptions for a company |
| GET | `/update-auto-renewal-toggle-off` | `@Auth()` | Manually trigger scheduler: disable auto-renewal for companies with no payment method |
| GET | `/:id/renewal-history` | `@Auth()` | Fetch renewal history for a subscription |
| GET | `/accounting-upgrades/analytics/pending-charge` | `@Auth()` | Sum of pending upgrade charge amounts |
| PUT | `/:id/update-delivery-status` | `@Auth()` | Update subscription-level delivery status |

### Service — `customer-subscription/services/customer-subscription.service.ts`

Key service calls and side-effects per operation:
- **updateServiceDeliveryStatus** — updates `servicedeliveries` record, recalculates aggregate `serviceDeliveryStatus` on `customersubscriptions`; propagates to same-FYE/same-code siblings when `subscriptionGroupingCriteria` matches; writes audit log.
- **updateCustomRenewalAmount** — patches `customRenewalAmount` + reason; audit log.
- **updateFinancialYearEnd** — recalculates `financialYearEnd` date from year param; audit log.
- **updateNextRenewalDate** — adjusts `nextRenewalDate`, recalculates `subscriptionRenewalStatus` (notDue if diff ≥ threshold); optionally reactivates auto-renewal.
- **toggleRenewal** — sets `isAutoRenewalEnabled`; audit log.
- **cancelRenewal** — sets status `cancelled`, disables auto-renewal; supports system-initiated cancel (no `user`).
- **reactivateSubscription** — restores `serviceDeliveryStatus` to `active` or `delivered`; clears offboarding reason.
- **offboardSubscription** — sets `serviceDeliveryStatus = toOffboard`.
- **discontinueSubscription** — sets `serviceDeliveryStatus = discontinued`; task sync via schema hook.
- **deleteCustomerSubscription** — hard delete via `customerSubscriptionRepository.deleteById`; audit log.
- **searchCustomerSubscriptions** — MongoDB aggregate with `$lookup` on `services` and `invoices`; paginated.
- **searchAccountingUpgrades** — aggregate filtered by `financialYearEnd` window (±3 years / +18 months).
- **massPatchCustomerSubscriptions** — CSV parsed with `csv-parse/sync`; validates against schema before bulk update.

### Schema — `customer-subscription/models/customer-subscription.schema.ts`

Collection: `customersubscriptions`

Key enums:
- `ServiceDeliveryStatus`: none, active, inactive, delivered, discontinued, toBeStarted, toOffboard, deactivated
- `SubscriptionRenewalStatus`: none, notDue, due, overdue, renewed, upgraded, downgraded, cancelled
- `RefundStatus`: none, pending, completed, failed
- `UpgradeStatus`: pendingCharge, failedCharge, cancelledCharge, noPaymentMethod, autoUpgraded, manualUpgraded, directDebitInprogress, cancelledVoided

### Schema — `customer-subscription/models/service-delivery.schema.ts`

Collection: `servicedeliveries`

Linked to `customersubscriptions` via `customerSubscriptionId`. Tracks individual deliverable status (`deliverableName`, `deliveryStatus`, `completionDate`, `deliveredByUserId`).
