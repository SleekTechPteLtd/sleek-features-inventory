# Pay pending invoices

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Pay pending invoices |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer (company admin) |
| **Business Outcome** | Customers can identify authorised invoices awaiting bank payment and proceed directly into the payment flow, enabling self-serve subscription renewal without support intervention. |
| **Entry Point / Surface** | Sleek App > Billing & Subscriptions > Renew Subscriptions > Pay Invoices (`PendingInvoicesPage`, back-nav: `renew-subscriptions` route) |
| **Short Description** | Displays all authorised invoices with a `PAY_BY_BANK` payment token for the customer's company. The customer selects an invoice to be forwarded to the token-based payment flow (`payment` route). |
| **Variants / Markets** | SG (SGD default currency); other markets Unknown |
| **Dependencies / Related Flows** | Upstream: `renew-subscriptions` flow; Downstream: token-based `payment` route; `generatePaymentToken` (POST `/payment-token`) used to create payment tokens earlier in the renewal flow; `createManualRenewalInvoice` (POST `/invoices/manual-renewal`) creates the invoice upstream |
| **Service / Repository** | customer-billing (frontend); sleek-billings-backend (REST API) |
| **DB - Collections** | Unknown (backend service; collections not visible from frontend proxy) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Are markets beyond SG (HK, UK, AU) supported — currency code is read from platform config but only SGD is evident as a default. 2. Is the `paymentToken` always pre-generated before reaching this page, or can it be created on-demand here? 3. Does the `PAY_BY_BANK` filter intentionally exclude card-payment invoices from this list? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/modules/sleek-billing/billing-and-subscriptions/pages/PendingInvoicesPage.vue`
- `src/proxies/back-end/sleek-billings-backend/sleek-billings-api.js`

### Key logic — `PendingInvoicesPage.vue`
- `mounted()` loads platform config to resolve `localization.value.currency_code` (default: `SGD`), then calls `fetchInvoices()`.
- `fetchInvoices()` retrieves `companyId` and `authToken` from `LocalStoreManager` (`@sleek/customer-common`), then calls `SleekBillingsAPI.getInvoicesByCompanyId` with:
  - `filter: '{"status": { $in: ["authorised"]}, "deleted":false, "type":"invoice"}'`
  - `populatePaymentToken: true`
- Result is further filtered client-side: only invoices where `status === 'authorised'` **and** `paymentToken.status === 'PAY_BY_BANK'` are shown.
- Clicking an invoice card calls `goToPayment(invoice.paymentToken.token)`, pushing to the `payment` named route with the token as a param.
- Back button navigates to the `renew-subscriptions` named route.

### API calls — `sleek-billings-api.js`
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/invoices?companyId=&limit=&filter=&populatePaymentToken=` | Fetch authorised invoices with payment token data |
| POST | `/payment-token` | Generate a payment token for an invoice (upstream step, `paymentOrigin: 'MANUAL_RENEWAL'`) |
| POST | `/invoices/manual-renewal` | Create a manual renewal invoice (upstream step) |

### Auth surface
- All API calls use a bearer token from `localStorage` (`id` key) or `LocalStoreManager.getToken()`.
- No role-based guard visible at the frontend layer; access control assumed to be enforced by sleek-billings-backend.
