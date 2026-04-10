# Manage Company Subscriptions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Company Subscriptions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Gives internal admins full visibility and control over a company's service subscriptions so they can monitor delivery health, act on upcoming renewals, and adjust subscription state without requiring engineering intervention. |
| **Entry Point / Surface** | Admin App > Company Billing > Subscriptions tab |
| **Short Description** | Admins browse, search, filter, sort, and act on all of a company's active and deactivated service subscriptions. The detail view exposes subscription-level actions: toggle auto-renewal, update renewal amount or date, cancel renewal, offboard, discontinue, reactivate, edit financial year end, and amend core fields (start/end date, delivery status, type of purchase, linked subscription). An audit log drawer surfaces the full change history per subscription. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | sleek-billings-api (customer-subscriptions, payment-methods, audit-logs endpoints); Xero (tax rates via `/xero/tax-rates`); Company Billing — Invoices & Credit Note tab; Company Billing — Credit Balance tab; Subscription renewal auto-charge pipeline; Offboarding request flow; Deliverables overview (DeliverablesOverviewSection component) |
| **Service / Repository** | sleek-website (frontend); sleek-billings-api (backend billing service, SLEEK_BILLINGS_API env) |
| **DB - Collections** | Unknown (proxied via sleek-billings-api; not directly accessible from frontend) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets are in scope (SG/HK/UK/AU)? Is `isMember` / `SLEEK_GROUP_NAMES` permission check the only gate for edit access, and which groups receive it? What triggers the `isExpanded` grouped-subscription display — is `subscriptionGroupingCriteria` set at the service-config level? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/views/admin/company-billing/index.js` — `AdminBillingConfigurationView`: root component; orchestrates tabs (Subscriptions / Invoices & Credit Note / Credit Balance); fetches company, users, services, tax rates, and all subscriptions on mount; passes company + user context down.
- `src/views/admin/company-billing/subscriptions-list.js` — `SubscriptionsList`: list view; search (subscription name, financial year, delivery status, renewal status), deactivated/discontinued toggle, expand-grouped toggle, multi-column sort (subscription name, end date, renewal status — cascading); auto-selects a subscription from `?subscriptionId=` URL param; navigates to `SubscriptionDetail` on row click.
- `src/views/admin/company-billing/subscription-detail.js` — `SubscriptionDetail`: detail/edit view; all mutation actions listed below; renders deliverables section (`DeliverablesOverviewSection`), linked subscription chain (`getAllTheNextLinkedSubscriptions`), invoice/credit-note items, audit log drawer.
- `src/views/admin/company-billing/constants.js` — delivery status values (`active`, `delivered`, `discontinued`, `inactive`, `toBeStarted`, `toOffboard`, `deactivated`), renewal status values (`notDue`, `due`, `overdue`, `renewed`, `upgraded`, `downgraded`, `cancelled`), purpose-of-purchase taxonomy (onboarding, renewal, upsell, upgrade subtypes, downgrade subtypes).

### API calls (via `src/utils/sleek-billings-api.js` → `SLEEK_BILLINGS_API`)
| Action | Method + Endpoint |
|---|---|
| List subscriptions | `GET /customer-subscriptions?companyId={id}` |
| Check payment method | `GET /payment-methods?companyId={id}` |
| View audit trail | `GET /audit-logs?companyId=&tags[]=subscription-{id}` |
| Update custom renewal amount | `PUT /customer-subscriptions/{id}/custom-renewal-amount` |
| Update next renewal date | `PUT /customer-subscriptions/{id}/next-renewal-date` |
| Cancel renewal | `PUT /customer-subscriptions/{id}/cancel-renewal` |
| Toggle auto-renewal | `PUT /customer-subscriptions/{id}/toggle-renewal` |
| Offboard subscription | `PUT /customer-subscriptions/{id}/offboard` |
| Reactivate subscription | `PUT /customer-subscriptions/{id}/reactivate` |
| Discontinue subscription | `PUT /customer-subscriptions/{id}/discontinue` |
| Update financial year end | `PUT /customer-subscriptions/{id}/financial-year-end` |
| Patch subscription data | `PUT /customer-subscriptions/{id}/patch-data` |

### Permissions
- `isMember(SLEEK_GROUP_NAMES.*)` check sets `hasEditPermission` — controls whether edit mode and mutation actions are available in the detail view.

### Subscription grouping logic
Subscriptions sharing the same `service.subscriptionGroupingCriteria` values (`same_item_code`, `same_fye`) are grouped in the table; the "Expand grouped subscriptions" toggle shows/hides historical rows within each group.

### Delivery status surface
Each subscription row shows a `serviceDeliveryStatus` chip mapped via `SUBSCRIPTION_DELIVERY_STATUS_MAPPING` and a `subscriptionRenewalStatus` chip mapped via `SUBSCRIPTION_RENEWAL_STATUS_MAPPING`. Auto-renewal is indicated with a `RepeatRoundedIcon` on the renewal status chip when `isAutoRenewalEnabled` is true and status is notDue/due/overdue.
