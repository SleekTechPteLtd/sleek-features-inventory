# Complete Payment and Continue Company Setup

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Complete payment and continue company setup |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer (new company registrant completing onboarding) |
| **Business Outcome** | Ensures customers successfully transition from payment to company incorporation or the main dashboard, with email verification gating for beta users to prevent unauthorized progression. |
| **Entry Point / Surface** | Sleek App > Billing > Payment Completion (`/billing/payment/completion?token=&paidWith=&origin=`) |
| **Short Description** | After completing payment, customers see a confirmation screen with CMS-driven onboarding steps and a "Continue Company Setup" CTA. For beta onboarding flows (`origin=betaOnboarding`), the system verifies email via payment token before routing to incorporation; for all other flows, routes directly to the customer dashboard. |
| **Variants / Markets** | SG, HK (zh locale explicitly handled for CMS step content); other markets Unknown |
| **Dependencies / Related Flows** | Platform CMS config (`sleek_site_onboarding > default_pages > payment_completion`); Email verification page (`/billing/payment/verification`); Company incorporation flow (`/customer/incorporate`); Customer dashboard (`/customer/dashboard`); Billing backend `GET /payment-token/{token}/is-user-verified` |
| **Service / Repository** | customer-billing; billing backend (microservice, URL resolved via `baseProxy.getBillingBackendUrl()`) |
| **DB - Collections** | Unknown (backend payment-token collection not visible from frontend proxy) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Is `betaOnboarding` origin still the primary onboarding path or a legacy flow? What markets beyond SG/HK are supported? What DB collection does the billing backend's `payment-token` endpoint touch? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `modules/sleek-billing/payment/pages/PaymentCompletion.vue`

- **Mounted lifecycle:**
  - Reads `paidWith` URL param; if `CREDIT_CARD`, sets `isCcPayment = true` to show payment confirmation heading.
  - Dispatches `configModule/GET_PLATFORM_CONFIG` to fetch CMS config, then extracts `sleek_site_onboarding.default_pages.payment_completion` for the onboarding steps list.
  - Supports `zh` locale for localized step content.
  - Pushes a browser history state and attaches a `popstate` handler to prevent back-button navigation.

- **`onClickedProceed()` — routing logic:**
  - Reads `token` and `origin` from URL query params.
  - If `origin === 'betaOnboarding'`:
    - Calls `PaymentServiceProxy.isUserVerified({ token })`.
    - `status === 'verified'` → `$router.push('/customer/incorporate?cid=...')`, saves `companyId` to `localStorage`.
    - `status === 'unverified'` → `$router.push('/billing/payment/verification?token=&email=...')`.
    - `status === 'retry'` → shows snackbar ("We are processing your request. Please retry again in few seconds.").
  - Otherwise → `$router.push('/customer/dashboard')`.

- **Navigation guard:** `beforeRouteLeave` blocks all programmatic navigation until `allowNavigation` flag is set by the proceed button.

### `proxies/back-end/subscriptions/payment.microservice.js`

- **`isUserVerified(input)`** — `GET ${billingBackendUrl}/payment-token/${token}/is-user-verified`
  - Returns `{ status: 'verified' | 'unverified' | 'retry', companyId?, email? }`.
  - Uses `preventDuplicatedRequest` guard (2000 ms debounce implied by pattern).
  - Auth: no `authToken` passed — uses unauthenticated request via payment token only.

- **`resendVerificationEmailUsingPaymentToken(input)`** — `GET ${billingBackendUrl}/payment-token/${token}/resend-verification-email`
  - Sibling method referenced in the verification page flow; surfaces the same payment token scope.
