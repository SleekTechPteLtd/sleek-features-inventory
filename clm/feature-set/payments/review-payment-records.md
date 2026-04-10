# Review payment records

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Review payment records |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations / Finance Admin |
| **Business Outcome** | Gives ops and finance teams a central place to browse and audit payment transactions, linking each payment back to its invoice so discrepancies can be spotted and billing collections monitored quickly. |
| **Entry Point / Surface** | Sleek Billings Admin > Billing > Payments (`/payments`) |
| **Short Description** | Table listing payment transactions with reference, customer, amount, status, payment method, transaction date, and linked invoice number. A search box is present for filtering records. Backend `Payment` model and API exist in sleek-billings-backend; frontend component integration is pending. |
| **Variants / Markets** | Unknown (sample data shows SGD; multi-market support not yet confirmed) |
| **Dependencies / Related Flows** | Invoices list (`/invoices`); Stripe payment processing; Xero reconciliation; `GET /v2/payment` list endpoint (not yet wired in UI) |
| **Service / Repository** | sleek-billings-frontend, sleek-billings-backend |
| **DB - Collections** | `payments` (MongoDB, sleek-billings-backend) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Low |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which backend API endpoint supplies payment records to the UI? `GetPaymentListRequestDto` exists but no controller route exposes a GET list. 2. Is search intended to be client-side or server-side? `searchQuery` state is set but not applied to the payments list render. 3. What actions does the per-row ellipsis menu expose? No handlers are implemented. 4. Which markets (SG, HK, UK, AU) does this cover? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Frontend — `sleek-billings-frontend`

- **Component**: `src/pages/Payments/PaymentsList.jsx`
  - Table columns: Reference, Customer, Amount, Status (badge), Payment Method, Transaction Date, Invoice (blue link text), Actions (ellipsis button — no handlers)
  - Search input: `searchQuery` state tracked via `useState('')` but not used to filter the `payments` array
  - Row data source: hardcoded sample array (one record: PAY-2023-001, VIC TEST Company, SGD 240.00, COMPLETED, Credit Card, 30/04/2025, INV-55113)
  - No API call; no import from `services/api.js`

- **Routing**: `src/App.jsx` line 162 — `<Route path="payments" element={<PaymentsList />} />`

- **Navigation**: `src/components/Navbar.jsx` line 118 — `{ path: '/payments', icon: CurrencyDollarIcon, label: 'Payments' }` under the "Billing" collapsible menu group

- **API service**: `src/services/api.js` — no `getPayments` or equivalent method; the closest related calls are `getInvoices` (`/invoices/`) and `getWebhooks` (`/webhooks`)

- **Build artifact**: `dist/assets/PaymentsList-CklrGHct.js` confirms the component is compiled and shipped

### Backend — `sleek-billings-backend`

- **Schema**: `src/payment/models/payment.schema.ts`
  - MongoDB collection: `payments` (inferred from Mongoose class name `Payment`)
  - Key fields: `companyId`, `status` (created / done / failed / canceled / requires_action), `paymentMethod` (instant_card / bank_transfer / cash / stripe_element / xero_payment), `amount`, `invoiceId`, `transactionId`, `referenceId`, `type` (auto_renewal / manual_renewal / payment_request / auto_upgrade / onboarding / reconcile / adhoc_request / repeating_invoice), `paidAt`, `paidBy`, `chargeId`, `chargeType` (stripe), `paymentIntentId`
  - Indexes on: `companyId + status + invoiceId + paymentMethod`, `invoiceId + status`, `referenceId + status`

- **DTOs**: `src/payment/dtos/get-payment-list.request.dto.ts`
  - Supports filtering by: `invoiceId`, `status`, `companyId`, `paymentIds`, `page`
  - Supports loading: `invoice` (relation)
  - `GetPaymentListResponseDto` returns an array of `Payment` documents

- **Controller**: `src/payment/controllers/payment-v2.controller.ts` (`@Controller('v2/payment')`)
  - POST endpoints for: `create-payment-intent`, `setup-intent`, `pay-with-payment-method`, `pay-with-card`, `pay-with-bank`, `preview-checkout`, `charge-payment-method`, `auto-charge-invoice-upgrade`
  - No GET list endpoint currently exposed via controller — `GetPaymentListRequestDto` exists in DTOs but is not yet routed

- **External integrations**: Stripe (charge processing), Xero (`xero_payment` method), SleekBillings MongoDB (via `sleek-service-delivery-api` for `customersubscriptions`, `invoices`, `companies`)
