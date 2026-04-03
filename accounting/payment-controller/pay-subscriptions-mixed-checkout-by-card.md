# Pay subscriptions and mixed checkout by card

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Pay subscriptions and mixed checkout by card |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User |
| **Business Outcome** | The company collects card revenue for subscription renewals, ad hoc billable lines, and payment-request checkouts while keeping Xero invoices and internal subscription state aligned. |
| **Entry Point / Surface** | Sleek customer app — Billings and subscriptions (`/billings-and-subscriptions`); payment flows initiated from renewal, mixed checkout, onboarding, or emailed payment links (payment token). |
| **Short Description** | Authenticated users pay with a saved company card via Stripe: charges run against stored card tokens, optionally after wallet credit is applied. Flows cover manual and automatic renewal, mixed subscription plus one-off lines, payment-request line items (with FYE-aware subscription date updates), accounting plan upgrade/downgrade hooks, and post-failure emails when auto-renewal cannot complete. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Stripe (charges, customers, balance transactions); Xero via invoice vendor for paid/unpaid invoices and fees; wallet/credit-balance handler (`credit-balance`); `auto-renewal-service`; `auto-upgrade-accounting` / `shiftAccountingCode` / `addBRService`; mailer templates; billing catalog from `billing-config-service` (Xero items or sleek-subscription microservice); optional `PaymentToken` for idempotent checkout. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | creditcards, paymenttokens, invoices, companies, users, companysubscriptionhistories, externalpaymentinfos, paymentrequests, billingconfigs |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact tenant/market mapping for `sharedData.tenant` is not fixed in these files; partner (`manage_service`) vs main Stripe client type behaviour should be confirmed per deployment. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controllers — `controllers/payment-controller.js`

- **`POST /payment/company-subscriptions`** (`userService.authMiddleware`): Subscription renewal checkout. Validates optional `payment_token` against `PaymentToken` (VALID → IN_PROGRESS; rejects duplicate processing). Body: `card_id`, `auto_renewal`, `is_last_attempt`. Loads subscriptions by `companySubscriptionIds`, filters to active recurring items from `billingConfigService.getXeroItems`, runs `upgradeAccountingSubscription`, `shiftAccountingCode`, `addBRService`. Builds invoice via `invoiceService.prepareInvoiceData`, creates/updates `Invoice` with tags `auto_renewal` / `manual_renewal`, `payment_method: instant_card`. Applies `autoRenewalService.preparePrePaymentData`; may `chargeUserFromCreditBalance` then `paymentService.chargeFromCard` with `entryPoint "auto-renewal"` when `auto_renewal` is true. On success: `updateExternalInvoice` or `createExternalInvoice`, `updateInvoicePostPayment`, `insertSubscriptionHistory` (auto vs manual renewal), deletes used `PaymentToken`, `sendEmailSubscriptionPaymentValidatedCreditCard`. On failure: `insertFailedRenewalSubscriptionHistory` for auto-renewal, token status `USED_PAYMENT_FAILED`, optional `sendEmailRenewalPaymentFailedCreditCard` / `sendEmailSubscriptionPaymentFailedCreditCard` when `is_last_attempt` and feature flags allow.

- **`POST /payment/all-types`** (`authMiddleware`): Mixed checkout — subscriptions from query `companySubscriptionIds` and/or `oneOffCodes`, plus optional `requestPaymentItems` / `requestPaymentId`. Same payment-token pattern. Uses `invoiceService.prepareOneOffAndSubscriptionInvoiceData` or `prepareInvoiceData`; may create subscriptions/updates from payment-request lines against `billingConfigService.getXeroCodesAndItems`; `companySubscriptionService.updateSubscriptionDatesBasedonFYERules` for FYE accounting rules. Card charge via `paymentService.chargeFromCard`; wallet pre-payment with `chargeUserFromCreditBalance(..., true)` for payment-request shape. `createExternalInvoice` / `updateExternalInvoice` with `requestPaymentItems`; `insertSubscriptionHistory` with `paymentRequest` type; confirmation email `sendEmailSubscriptionPaymentValidatedCreditCard`.

- **`POST /payment/manual-payment-request`**: Bank transfer / cash path for payment requests (not card) — listed as related surface for payment-request line items; uses `ExternalPaymentInfo`, not Stripe card charge in the main branch shown.

- **`POST /payment/create-company/:companyId`**, **`/payment/onboarding/:companyId`**, and other routes: Additional card charges via `paymentService.chargeFromCard` for incorporation/onboarding payments (same controller file).

- **`POST /payment/remind-company-renewal-subscriptions-without-cc`**: Follow-up when renewal cannot charge without a card (reminder path; complements failure emails).

### Services — `services/payment-service.js`

- Stripe: `getStripe` / `getUserStripeField` for `main` vs `manage_service`; `chargeFromCard`, `charge`, `loopChargeFromCards`, `chargeUserFromCards`, `chargeFromCompanyCards` with `entryPoint` `"auto-renewal"` / `"auto-upgrade"` for decline handling via `checkErrResponse` and `updateCardStatus` on `CreditCard` documents; `createUserCard`, audit via sleek-auditor; `getTransactionFromCharge` for Stripe balance transaction; `chargeUserFromCreditBalance` / `refundUserCreditBalance` delegating to wallet handler for AC/CO credit balance item codes.

### Services — `services/invoice-service.js`

- `prepareInvoiceData`, `prepareOneOffAndSubscriptionInvoiceData`, `getItemsFromSubscription`, `createExternalInvoice`, `updateExternalInvoice`, `getModifiedItems` for `requestPaymentItems` line overrides; integrates `paymentService.getTransactionFromCharge`, Xero fee line `createFee`, `billingConfigService` for catalog.

### Services — `services/company-subscription-service.js`

- Post-payment: `refreshSubscription`, `sendEmailSubscriptionPaymentValidatedCreditCard`, `sendEmailSubscriptionPaymentValidatedTransfer`, `sendEmailSubscriptionPaymentFailedCreditCard`, `sendEmailRenewalPaymentFailedCreditCard` (decline-specific copy), `insertSubscriptionHistory`, `insertFailedRenewalSubscriptionHistory`, `updateSubscriptionDatesBasedonFYERules`, `resolveFinalCompanyStatusDuringPayment`; uses `billingConfigService.getXeroItems` / `getXeroCodesAndItems`.

### Services — `services/billing-config-service.js`

- `getXeroItems` (Xero OAuth items + `BillingConfig` mongo or sleek-subscription microservice when feature flag); `getXeroCodesAndItems`; `isUpdateSubscriptionDates` for financial-year accounting items.

### Schemas (Mongo)

- `schemas/credit-card.js` → **creditcards**; `PaymentToken`, `Invoice`, `Company`, `User`, `ExternalPaymentInfo`, `PaymentRequest`, `CompanySubscriptionHistory`, `BillingConfig` as referenced in controller/services.
