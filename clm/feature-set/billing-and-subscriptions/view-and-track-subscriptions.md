# View and track subscriptions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | View and track subscriptions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Customers have full visibility into their active and past service subscriptions, allowing them to monitor renewal obligations and act before services lapse. |
| **Entry Point / Surface** | Sleek App > Billings & Subscriptions > My Subscriptions tab |
| **Short Description** | Displays a filterable, searchable table of current and past service subscriptions showing subscription name, financial year, start/end dates, and renewal status (Overdue, Due, Not due, Renewed, Upgraded, Downgraded, Cancelled). Auto-renewal and one-time subscription indicators are shown inline. Overdue and due items are pinned to the top. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Billing History tab (BillingHistoryContent.vue), Payment Methods tab (PaymentMethodsContent.vue), Renew Subscriptions flow (renew-subscriptions route / RenewSubscriptionsPage.vue), sleek-billings-backend API |
| **Service / Repository** | customer-billing (frontend), sleek-billings-backend (API) |
| **DB - Collections** | Unknown (frontend only; backend repo not in scope) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets are served? No market-specific logic visible. What collections does the billing backend use? The "Credit balance" tab is commented out in BillingsAndSubscriptionsContent.vue — deprecated or planned? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `BillingAndSubscriptionsContainer.vue` — wraps content in `MasterLayout` from `@sleek/customer-common`; registers `BillingsAndSubscriptionsContent` and a `<router-view>` for nested pages

### UI / interaction (BillingsAndSubscriptionsContent.vue)
- Tab layout: **My subscriptions**, **Billing history**, **Payment methods** (Credit balance tab commented out)
- Segmented toggle — **Current** vs **Past** — filters rows by end date relative to today and renewal status:
  - Current: end date in future, or end date past but status is Due/Overdue
  - Past: end date past and status is NOT Due/Overdue
- Freetext search filters on `sub.name`
- Inactive services (`service.status === 'inactive'`) are excluded
- Sort order: Overdue → Due → other, then by start date descending, then by `serviceDeliveryStatus` priority (`active` → `toBeStarted` → `delivered` → `toOffboard` → `discontinued`), then alphabetically
- "Renew subscriptions" button links to `{ name: 'renew-subscriptions' }` route
- Tab selection persisted in URL query param `?tab=subscriptions|history|payment`

### Subscription row columns rendered
| Column | Source field |
|---|---|
| Subscription | `service.name` |
| Service FY | `financialYearEnd` → `FY YYYY` |
| Start date | `subscriptionStartDate` (formatted DD/MM/YYYY) |
| End date | `subscriptionEndDate` (formatted DD/MM/YYYY) |
| Renewal status | `subscriptionRenewalStatus` mapped to: Overdue, Due, Not due, Renewed, Upgraded, Downgraded, Cancelled, N/A |

- Auto-renewal icon (sync icon) shown when `isAutoRenewalEnabled === true` and status is Overdue/Due/Not due
- One-time subscription info icon shown when `service.recurring === false`

### API call
- Proxy: `SleekBillingsAPI.getSubscriptionsByCompanyId()`
- Endpoint: `GET {billingBackendUrl}/customer-subscriptions?companyId={companyId}`
- Auth: Bearer token from `localStorage.getItem('id')` or `LocalStoreManager.getToken()`
- Company resolution: `LocalStoreManager.getCompanyId()`
- Proxy file: `src/proxies/back-end/sleek-billings-backend/sleek-billings-api.js`
