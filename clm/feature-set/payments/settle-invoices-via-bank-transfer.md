# Settle Invoices via Bank Transfer

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Settle invoices via bank transfer |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client |
| **Business Outcome** | Clients who cannot or prefer not to pay by card can receive emailed bank transfer instructions and settle outstanding invoices manually, ensuring Sleek can collect payment from a broader set of clients |
| **Entry Point / Surface** | Sleek App > Incorporate > Payment Step; Sleek App > Billing & Subscriptions > Payment |
| **Short Description** | Clients switch from credit/debit card to bank transfer during checkout. They submit an expected payment date and optional cheque number; the system emails Sleek's bank account details and invoice number to the client, then redirects them to Billing & Subscriptions. |
| **Variants / Markets** | SG (SGD currency hardcoded) |
| **Dependencies / Related Flows** | Credit card payment (alternate path in same Payment component); Billing & Subscriptions renewal flow; Admin subscription management (tracks `expected_external_payment_info` status: processing / done); Coupon/promo code locking (shared with card payment path) |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown (state persisted server-side via `expected_external_payment_info` on company/subscription; localStorage key `emailSentForManualPayment` set client-side) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which backend service sends the email and generates the invoice? Not visible from frontend code. 2. Does the `PUT /companies/{id}/apply-for-external-payment` endpoint also send the email, or is that a separate job? 3. Is this flow available in HK, UK, or AU, or strictly SG (SGD is hardcoded in the Payment component)? 4. The `applyForExternalPayment` (subscription-level) and `applyForCompanyExternalPayment` (company-level) are two distinct API calls — which contexts trigger each? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/components/payment/payment.js` — Top-level payment wrapper. Renders `CreditCard` or `BankTransfer` sub-component based on `selectedPaymentMethod` state (default: `"card"`). Method `getPaymentMethod()` locks to `"bank"` if `externalPaymentInfo` prop is non-null. Method `onSubmitBankTransferForm()` validates `expected_pay_at`, then calls `props.applyForExternalPayment(payload)`.
- `src/components/payment/bank-transfer.js` — Two-mode component:
  - **Mode 1** (`externalPaymentInfo == null`): Form collecting `expected_pay_at` (required) and `cheque_number` (optional). Shows explanatory copy: *"an email with an invoice number, Sleek's bank account number and other details … would be sent to {user.email}"*.
  - **Mode 2** (`externalPaymentInfo != null`): Read-only display of invoice number (with PDF link), approximate payment date, and cheque number. Instruction to include name + invoice number in transfer comments.
- `src/views/incorporate/steps/payment-step.js` — Hosts `Payment` in the company incorporation wizard. Implements `applyForExternalPayment()`: calls `api.applyForCompanyExternalPayment(companyId, payload)` (`PUT /companies/{id}/apply-for-external-payment`), shows spinner ("Emailing Payment Instructions…"), sets `emailSentForManualPayment` in localStorage, then redirects to `/billings-and-subscriptions/`.

### API calls (from `src/utils/api.js`)
- `PUT /companies/{companyId}/apply-for-external-payment` — used in the incorporation flow (`applyForCompanyExternalPayment`)
- `PUT /company-subscriptions/{companySubscriptionId}/apply-for-external-payment` — used for single-subscription renewal (`applyForExternalPayment`)
- `POST /company-subscriptions/apply-for-external-payment` — used for multi-subscription renewal (`applyForExternalPaymentForMultipleSubscriptions`)

### State shape
`expected_external_payment_info` (on company or subscription):
```
{
  invoices: [{ number, url, status }],  // status: "done" | "processing"
  expected_pay_at: "<date string>",
  cheque_number: "<string | null>"
}
```

### Admin visibility
- `src/views/admin/subscriptions/new/components/table.js`: `isManualPaymentMade()` checks for `expected_external_payment_info.invoices.0` to flag subscriptions awaiting manual payment.
- `src/views/admin/subscriptions/new/details/components/history.js`: Renders history differently when `expected_external_payment_info` is present or invoice status is `"done"` / `"processing"`.

### Currency
Payment currency is hardcoded to `"SGD"` in `payment.js` (`this.paymentCurrencyCode = "SGD"`), suggesting this flow is primarily Singapore-scoped.
