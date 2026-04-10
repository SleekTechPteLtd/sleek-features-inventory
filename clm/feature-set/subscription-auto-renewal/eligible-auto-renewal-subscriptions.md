# View Eligible Auto-Renewal Subscriptions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | View Eligible Auto-Renewal Subscriptions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators can identify which client subscriptions will auto-renew within the next 30 days to support proactive account management and charge preparation. |
| **Entry Point / Surface** | Internal Billing API > `GET /subscription-auto-renewal/eligible/:companyId` |
| **Short Description** | Returns all subscriptions for a given company that have auto-renewal enabled and a next renewal date within the next 30 days, with a renewal status of notDue, due, or overdue. Populates the associated service details for each result. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Trigger Auto-Renewal Charge, Trigger Auto-Renewal Early Reminders, Trigger Auto-Renewal Charge Reminders (all in subscription-auto-renewal module) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | customersubscriptions |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | No market-specific filtering in query — unclear if results differ across SG/HK/UK/AU. No pagination on the endpoint; could be a concern for large companies. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller
`src/customer-subscription/controllers/subscription-auto-renewal.controller.ts`

- `GET /subscription-auto-renewal/eligible/:companyId` (line 39–43)
- Guard: `@Auth()` — requires authenticated session; no group-level restriction (accessible to all authenticated internal users)
- Delegates to `SubscriptionAutoRenewalService.getEligibleRenewals(companyId)`

### Service
`src/customer-subscription/services/subscription-auto-renewal.service.ts`

- `getEligibleRenewals(companyId)` (lines 723–742)
- Query filter:
  - `isAutoRenewalEnabled: true`
  - `nextRenewalDate` between today (start of day) and today +30 days (end of day)
  - `subscriptionRenewalStatus` in `[notDue, due, overdue]`
  - `populate: ['service']` — hydrates the linked service document
- No additional filtering by service duration, service status, or client type (unlike the internal `getSubscriptionsForAutoRenewal` helper used for charge/reminder triggers)

### Schema / Collections
- `CustomerSubscription` model → collection: `customersubscriptions`
  - Key fields referenced: `companyId`, `isAutoRenewalEnabled`, `nextRenewalDate`, `subscriptionRenewalStatus`, `service` (ref)
- `SubscriptionRenewalStatus` enum: `notDue`, `due`, `overdue`, `renewed`, `upgraded`, `downgraded`, `cancelled`
