# Create Payment Request

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Create Payment Request |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (Sales Admin, Billing Operations Admin, Billing Super Admin) |
| **Business Outcome** | Enables internal admins to generate and send invoices to client companies for Sleek services, with the ability to charge an existing payment method on file immediately. |
| **Entry Point / Surface** | **sleek-website** admin app — **`/admin/company-billing/?tab=0`** — **Payment Request** opens **`InvoiceForm`** (invoice composer). |
| **Short Description** | Admin selects service line items, applies tax rates and optional discounts, sets purpose of purchase per line (onboarding, renewal, upgrade, etc.), and submits the invoice to Xero. Once authorised, the invoice can be sent via email link or charged directly against the company's saved payment method (card or direct debit). |
| **Variants / Markets** | SG, HK, UK, AU (platform config controls currency and tax calculation mode — UK uses exclusive tax, others inclusive) |
| **Dependencies / Related Flows** | Xero (invoice creation, tax rates); SleekBillings payment service (invoice CRUD, charge, subscriptions, credit balance, payment methods); Stripe (card validation/charge); Company Subscriptions; Credit Balance; Coupon/Discount engine |
| **Service / Repository** | sleek-website (admin frontend); SleekBillings payment service (backend API) |
| **DB - Collections** | Unknown — managed by SleekBillings payment service; likely includes invoices, customer-subscriptions, payment-methods collections |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which service owns the invoice MongoDB collections? Does chargePaymentMethod go through Stripe directly or via a SleekBillings abstraction? Is the Xero invoice creation synchronous or queued? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `src/views/admin/company-billing/index.js:64` — `handlePaymentRequestClick` sets `showInvoiceCreator: true`; "Payment Request" button at the top of the Company Billing page
- `src/views/admin/company-billing/index.js:175` — renders `<InvoiceForm>` when `showInvoiceCreator` is true

### Form component
- `src/views/admin/company-billing/invoice-form.js:62` — `InvoiceForm` component; accepts `company`, `allServices`, `allTaxRates`, `companySubscriptions`, `companyUsers`
- Line items: service code + name, description, quantity, unit price, custom price, tax rate, discount (flat or %), purpose of purchase, linked existing subscription, financial year
- Line amount type: inclusive or exclusive of tax (driven by `billing_service.taxCalculation` platform config flag)

### API calls (via SleekBillings payment service)
- `POST /invoices` — `updateOrCreateInvoice` (create or update invoice draft, generate Xero invoice, or send payment request email); `invoiceOrigin: 'paymentRequest'` — `invoice-form.js:1294`
- `POST /v2/payment/charge-payment-method` — `chargePaymentMethod`, charges saved card or direct debit; restricted to Sales Admin / Billing Operations Admin / Billing Super Admin — `invoice-form.js:1373`
- `GET /subscription-config?clientType=main|manage_service` — load service catalogue for payment request — `index.js:323`
- `GET /xero/tax-rates` — load Xero tax rates — `index.js:336`
- `GET /customer-subscriptions` — load company subscriptions to link line items — `index.js:345`
- `GET /customer-payment-methods` — validate whether a saved, non-expired card or direct debit is on file — `invoice-form.js:510`
- `GET /credit-balance` — fetch company credit balance to determine chargeability — `invoice-form.js:553`

### Permission guard
- `src/views/admin/company-billing/invoice-form.js:525-547` — `checkChargePaymentMethodPermission` checks group membership for `SALES_ADMIN`, `BILLING_OPERATIONS_ADMIN`, `BILLING_SUPER_ADMIN` before enabling the "Charge Payment Method" action

### Invoice lifecycle
- Draft → (generate Xero invoice) → Authorised → (charge or send link) → Paid / ddInProgress / Failed
- `INVOICE_ORIGIN_VALUES.paymentRequest` — `constants.js:231` — distinguishes admin-created invoices from autoRenewal, manualRenewal, reconcile, betaOnboarding origins
- Auto-renewal and manual-renewal draft invoices have form editing disabled — `invoice-form.js:600`

### Key constants
- `src/views/admin/company-billing/constants.js` — `INVOICE_ORIGIN_VALUES`, `INVOICE_STATUSES`, `PURPOSE_OF_PURCHASE_VALUES`, `DISCOUNT_TYPE_OPTIONS`, `LINE_AMOUNT_TYPES`
- `src/utils/constants.js:1587` — `SLEEK_GROUP_NAMES` including `BILLING_SUPER_ADMIN`, `BILLING_OPERATIONS_ADMIN`, `SALES_ADMIN`
