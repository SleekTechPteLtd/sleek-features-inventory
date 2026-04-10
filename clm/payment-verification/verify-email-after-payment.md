# Verify Email After Payment

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Verify Email After Payment |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer (Subscriber) |
| **Business Outcome** | Ensures a customer's email address is confirmed after completing a subscription payment, unblocking full activation of the subscription. |
| **Entry Point / Surface** | Sleek App > Billing > Payment Verification Page (post-payment redirect with `?token=…&email=…` query params) |
| **Short Description** | After completing a bank/non-CC payment, customers land on a verification page prompting them to confirm their email. They can resend the verification email via a one-time payment token. Credit-card payments bypass this step and display an immediate subscription confirmation. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Billing backend: `GET /payment-token/:token/resend-verification-email`, `GET /payment-token/:token/is-user-verified`; upstream payment flows (pay-with-bank, pay-with-card); subscription activation flow; `/billing/billing-and-subscriptions/` dashboard |
| **Service / Repository** | customer-billing |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which backend service owns the `/payment-token` endpoints? What sets the `isCcPayment` flag — route param or parent component? What collections/fields track email verification state on the backend? Are there markets where this step is skipped or handled differently? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Frontend — `modules/sleek-billing/payment/pages/PaymentVerificationPage.vue`

- Renders two states controlled by `isCcPayment` data flag:
  - **CC payment**: shows "Thank you! Your subscription has been confirmed." (no email action needed)
  - **Non-CC payment**: shows i18n text `$payment_ui.post_verification.verify_your_email_text` with customer email interpolated; displays a **Resend email** button
- `onResendClicked()` reads `?token` from URL query params and calls `PaymentServiceProxy.resendVerificationEmailUsingPaymentToken({ token })`
  - On HTTP 500 or 422 → redirects to `/customer/dashboard`
  - On success → snackbar: "Verification email has been resent successfully"
  - On thrown error → snackbar error + redirect to `/customer/dashboard`
- `mounted()` reads `?email` from URL query params to display the customer's email address
- On proceed: navigates to `/billing/billing-and-subscriptions/?cid=<companyId>` via `LocalStoreManager`

### Proxy — `proxies/back-end/subscriptions/payment.microservice.js`

- `resendVerificationEmailUsingPaymentToken(input)`:
  - `GET ${billingBackendUrl}/payment-token/${input.token}/resend-verification-email`
  - Auth token: `null` (unauthenticated; token in path serves as credential)
  - Wrapped in `preventDuplicatedRequest` guard

- `isUserVerified(input)`:
  - `GET ${billingBackendUrl}/payment-token/${input.token}/is-user-verified`
  - Auth token: `null` (same pattern)
  - Not currently called from `PaymentVerificationPage.vue` — may be used elsewhere or is dead code
