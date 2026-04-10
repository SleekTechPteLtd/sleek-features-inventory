# Request Bank Transfer Payment Instructions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Request Bank Transfer Payment Instructions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client (authenticated company representative) |
| **Business Outcome** | Allows clients who cannot or prefer not to pay by card to submit their intended payment date and receive Sleek's bank account details by email, enabling offline bank transfer or cheque payment for subscription renewals. |
| **Entry Point / Surface** | Sleek Website > Billing & Subscriptions > Subscription Renewal payment screen > "Bank Transfer / Cheque" payment option |
| **Short Description** | When a client selects the bank transfer payment method on the subscription renewal screen, they enter an expected payment date (required) and an optional cheque number, then click "Email Me Payment Instructions". The system sends an email to the client's registered address containing Sleek's bank account number, the invoice number, and other payment details. If instructions have already been sent, the screen switches to a read-only view displaying the invoice number, approximate payment date, and cheque number. |
| **Variants / Markets** | SG (currency hardcoded to SGD; other markets Unknown) |
| **Dependencies / Related Flows** | Subscription renewal flow (payment screen host); credit card payment (alternate path on same screen); promo code / coupon locking; backend API `POST /company-subscriptions/apply-for-external-payment` |
| **Service / Repository** | sleek-website; backend service handling `/company-subscriptions/apply-for-external-payment` (repo Unknown) |
| **DB - Collections** | Unknown (no direct DB access in frontend; backend persists `expected_external_payment_info` on the company-subscription record) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which backend repo/service handles `POST /company-subscriptions/apply-for-external-payment` and sends the email? What email template is used? Is this available in HK/UK/AU markets or SG-only (SGD is hardcoded in the payment component)? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files read
- `src/views/payments/index.js` — `Payments` view; orchestrates the subscription renewal payment screen. Calls `api.applyForExternalPaymentForMultipleSubscriptions` with `companySubscriptionIds` (query) and `{ expected_pay_at, cheque_number }` (body). On success stores `emailSentForManualPayment` in local store and redirects to `/billings-and-subscriptions/`.
- `src/components/payment/payment.js` — `Payment` component; toggles between card and bank-transfer sub-forms. When `externalPaymentInfo` prop is non-null the form is locked to the bank view (read-only confirmation state). "Email Me Payment Instructions" button triggers `onSubmitBankTransferForm`, which validates `expected_pay_at` is present before calling `props.applyForExternalPayment`.
- `src/components/payment/bank-transfer.js` — `BankTransfer` component; renders a date picker (`expected_pay_at`, required) and an optional cheque number text field for submission. When `externalPaymentInfo` prop is set, renders a read-only table showing invoice number (with PDF link), approximate payment date, and cheque number.

### Key API call
```
POST /company-subscriptions/apply-for-external-payment
  ?companySubscriptionIds[]=<id>&...
  Body: { expected_pay_at: "YYYY-MM-DD", cheque_number: "<optional>" }
```
Defined in `src/utils/api.js:1546` (`applyForExternalPaymentForMultipleSubscriptions`).

### State after submission
`externalPaymentInfo` on the subscription record (field `expected_external_payment_info`) is populated by the backend and surfaced via `getSubscriptionsPrice`. Once set, the payment screen renders the read-only confirmation view with invoice number and payment date instead of the submission form.

### Loading state
`views/payments/index.js` renders a full-page spinner with the message "Emailing Payment Instructions…" while the API call is in flight (`emailingInProgress` state flag).
