# Renew Subscriptions Manually

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Renew Subscriptions Manually |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Enables customers to self-serve subscription renewals by selecting due or overdue subscriptions and paying through a generated invoice and payment token, reducing reliance on Sleek staff for manual billing. |
| **Entry Point / Surface** | Customer Billing App > Billing & Subscriptions > Renew Subscriptions |
| **Short Description** | Customers review their due, overdue, and not-yet-due subscriptions, select one or more to renew (subscriptions with direct debit already in progress are locked), and initiate payment via a two-step backend flow: create a manual renewal invoice, then generate a payment token that redirects to the payment page. |
| **Variants / Markets** | SG (amount formatting uses `en-SG` locale; currency code is config-driven suggesting possible multi-market intent) |
| **Dependencies / Related Flows** | Upstream: Billing & Subscriptions overview (`billing-and-subscriptions` route); Downstream: Payment page (token-based, `payment` route); Related: Pending Invoices page (linked from pay-by-bank warning banner); sleek-billings-backend service; `@sleek/customer-common` shared library |
| **Service / Repository** | customer-billing, sleek-billings-backend |
| **DB - Collections** | Unknown — frontend proxy delegates to sleek-billings-backend; no direct DB access visible in this code |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Is `en-SG` locale hardcoding intentional or a bug for HK/AU customers? Currency code is config-driven but amount display is not. 2. Who sets `customRenewalAmount` on a subscription and when does it take precedence over `service.price`? 3. What MongoDB collections does sleek-billings-backend use for invoices and subscriptions? 4. Is the `payment` route and token-based payment page covered by a separate feature doc? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### UI — `modules/sleek-billing/billing-and-subscriptions/pages/RenewSubscriptionsPage.vue`

- Page renders a selectable table of subscriptions filtered to statuses `Not due`, `Due`, `Overdue` with `serviceDeliveryStatus !== 'inactive'`.
- Subscription status is mapped from `subscriptionRenewalStatus` field: `overdue`, `due`, `notDue`, `renewed`, `upgraded`, `downgraded`, `cancelled`, `none`.
- Subscriptions with `serviceId` in `ddInProgressItemsIds` are visually dimmed and their checkboxes are disabled — prevents duplicate payment for direct debit in-flight.
- Subscriptions with `PAY_BY_BANK` payment tokens show a banner linking to the pending invoices page.
- Footer shows count of selected items and running total (`customRenewalAmount ?? service.price`).
- `handlePayment()` (line 359) orchestrates two sequential API calls:
  1. `createManualRenewalInvoice` → POST `/invoices/manual-renewal`
  2. `generatePaymentToken` → POST `/payment-token`
  Then pushes to `{ name: 'payment', params: { token: paymentResponse.token } }`.
- Currency code sourced from platform CMS config (`localization.value.currency_code`) at mount time.

### API Proxy — `proxies/back-end/sleek-billings-backend/sleek-billings-api.js`

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/customer-subscriptions?companyId=` | Fetch all subscriptions for the company |
| GET | `/invoices?companyId=&limit=&filter=&populatePaymentToken=` | Fetch existing invoices (detect ddInProgress / payByBank) |
| POST | `/invoices/manual-renewal` | Create renewal invoice; payload: `{ companyId, invoiceOrigin: 'manualRenewal', subscriptions: [...] }` |
| POST | `/payment-token` | Generate payment token; payload: `{ invoice: invoiceId, companyId, paymentOrigin: 'MANUAL_RENEWAL' }` |

- `invoiceOrigin: 'manualRenewal'` and `paymentOrigin: 'MANUAL_RENEWAL'` distinguish this flow from auto-renewal in the backend.
- Invoice filter on fetch: `{ status: { $in: ["authorised", "ddInProgress"] }, deleted: false, type: "invoice" }`.
- Auth via `authToken` from `localStorage.getItem('id')` or `LocalStoreManager.getToken()`.
