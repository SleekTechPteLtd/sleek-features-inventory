# Renew Subscriptions and Pay Invoices

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Renew Subscriptions and Pay Invoices |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer (company user) |
| **Business Outcome** | Enables customers to renew due or overdue service subscriptions by creating a manual renewal invoice and completing payment, ensuring uninterrupted service delivery. |
| **Entry Point / Surface** | Customer App > Billing & Subscriptions > Renew Subscriptions; Customer App > Billing & Subscriptions > Pending Invoices |
| **Short Description** | Customers select one or more due, overdue, or upcoming subscriptions for renewal. The app creates a manual renewal invoice, generates a payment token, and routes the user to the payment page. Supports card, direct debit, and bank transfer. Subscriptions with an in-progress direct debit payment are locked from re-selection. Bank-transfer invoices awaiting bank confirmation are tracked on a separate Pending Invoices page. |
| **Variants / Markets** | Unknown — currency code is config-driven (`localization.currency_code`); UI defaults to `en-SG` formatting, suggesting SG at minimum; other markets unconfirmed from this repo |
| **Dependencies / Related Flows** | Billing backend service (`sleek-billings-backend`): `/customer-subscriptions`, `/invoices/manual-renewal`, `/payment-token`, `/invoices`; Payment page flow (`payment` route, `PaymentRequestMicroservice`); Platform config (`configModule/GET_PLATFORM_CONFIG`) for currency localisation; `@sleek/customer-common` (LocalStoreManager, auth) |
| **Service / Repository** | customer-billing |
| **DB - Collections** | Unknown — frontend only; collections owned by sleek-billings-backend |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets/currencies are live beyond SG? Does a credit balance offset apply before invoice creation? What is the backend repo implementing `/invoices/manual-renewal` and `/payment-token`? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Pages
- `modules/sleek-billing/billing-and-subscriptions/pages/RenewSubscriptionsPage.vue`
  - Fetches subscriptions via `SleekBillingsAPI.getSubscriptionsByCompanyId` → `GET /customer-subscriptions?companyId=…`
  - Fetches invoices via `SleekBillingsAPI.getInvoicesByCompanyId` → `GET /invoices?companyId=…&filter={"status":{"$in":["authorised","ddInProgress"]},"deleted":false,"type":"invoice"}&populatePaymentToken=true`
  - Identifies `ddInProgress` invoice items → disables those subscriptions from selection
  - Identifies `PAY_BY_BANK` (bank transfer) invoice items → shows "View pending invoices" banner
  - On "Proceed to pay":
    1. `SleekBillingsAPI.createManualRenewalInvoice` → `POST /invoices/manual-renewal` with `{ companyId, invoiceOrigin: 'manualRenewal', subscriptions: [...] }`
    2. `SleekBillingsAPI.generatePaymentToken` → `POST /payment-token` with `{ invoice, companyId, paymentOrigin: 'MANUAL_RENEWAL' }`
    3. Routes to `payment` page with `params: { token: paymentResponse.token }`
  - Subscription renewal statuses: `overdue`, `due`, `notDue`, `renewed`, `upgraded`, `downgraded`, `cancelled`
  - Filters renewable subscriptions: statuses `Due | Overdue | Not due` AND `serviceDeliveryStatus !== 'inactive'`

- `modules/sleek-billing/billing-and-subscriptions/pages/PendingInvoicesPage.vue`
  - Fetches authorised invoices with `populatePaymentToken=true`
  - Filters to `status === 'authorised' && paymentToken.status === 'PAY_BY_BANK'` — bank transfer invoices awaiting confirmation
  - Each invoice card navigates to `payment` route via `paymentToken.token`

### API Proxy
- `proxies/back-end/sleek-billings-backend/sleek-billings-api.js`
  - `getSubscriptionsByCompanyId` → `GET /customer-subscriptions`
  - `createManualRenewalInvoice` → `POST /invoices/manual-renewal`
  - `generatePaymentToken` → `POST /payment-token`
  - `getInvoicesByCompanyId` → `GET /invoices`

### Payment continuation
- `modules/sleek-billing/payment/pages/PaymentPage.vue` — payment completion handled by `PaymentRequestMicroservice`; listens for `BILLING_EVENTS.ON_RENDER_PAYMENT_PAGE` to receive `subscriptionIds`, `task`, `requestPaymentId`, `requestPaymentItems`
