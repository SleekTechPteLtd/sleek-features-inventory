# Run payment request auto-charge batch

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Run payment request auto-charge batch |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Eligible payment requests are collected on company saved cards (after credits) without a customer manually opening the payment link, and successfully paid requests are marked used so finance state stays accurate. |
| **Entry Point / Surface** | Authenticated HTTP API: `POST /v2/auto-charge-payment-requests/trigger-process`. The same batch logic is also runnable as a Node script (`scripts/autoChargePaymentRequests.js`) for scheduled jobs. Related: operators may adjust a request’s effective batch date via `POST /v2/auto-charge-payment-requests/update-date` (see `align-payment-request-date-for-auto-charge.md`). |
| **Short Description** | Loads **NEW** payment requests whose `createdAt` falls on the calendar day **two days before** the run; for each, finds the user by email and non-declined, unexpired company cards (primary first), applies available wallet credits to line items (`applyAvailableCompanyCreditBalance`), creates a short-lived `PaymentToken`, and charges through `paymentAllTypes` (same path as standard card checkout). On HTTP 200 from that flow, sets the payment request status to **USED** and records success metadata; tries cards in order until one succeeds. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `payment-all-types.service` (Stripe card charge, invoices, subscriptions history, emails as in other card checkouts); `applyAvailableCompanyCreditBalance` in `handlers/payment-requests/details` (wallet `getWalletBalanceService`, Xero one-off credit lines via `invoiceService.getOneOffItemsFromXero`); `credit-card-service.sanitizeCreditCards`; `userService.generateToken`; partner companies use `manage_service` client type vs `main`. Cross-feature: manual payment-request pay-by-link flows share `PaymentRequest` and payment stack. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | paymentrequests, users, companies, creditcards, paymenttokens; plus collections touched inside `paymentAllTypes` (e.g. invoices, companysubscriptionhistories, externalpaymentinfos, billingconfigs — same as mixed card checkout). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether every environment schedules `autoChargePaymentRequests.js` or relies mainly on the HTTP trigger; exact operator UI or runbook for the batch. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Router — `app-router.js`

- Mounts **`/v2/auto-charge-payment-requests`** → `controllers-v2/auto-charge-payment-requests`.

### Controllers — `controllers-v2/auto-charge-payment-requests.js`

- **`POST /trigger-process`** (`userService.authMiddleware`): delegates to `triggerAutoChargePaymentRequests`.

### Handlers — `controllers-v2/handlers/payment-requests/auto-charge-payment-requests.js`

- **`triggerAutoChargePaymentRequests`**: `const paymentRequests = await chargePaymentRequests();` → `res.status(200).json({ payment_requests: paymentRequests })` (successful charge summaries returned from the service).

### Service — `services/auto-charge-payment-request-service.js`

- **`getNewPaymentRequests`**: `PaymentRequest.find` with `createdAt` between start and end of **the day that is two calendar days before today** (`moment().add(-2, 'day')`), and `status: NEW`. Returns a **cursor** for streaming.
- **`chargePaymentRequests`**: Iterates each PR with `eachAsync`; loads `User` by `paymentRequest.email`; loads `CreditCard` for `paymentRequest.company` with `expire_at > now`, `status` not in `DECLINE_CODES`, sorted `is_primary` desc then `expire_at` desc; `sanitizeCreditCards`.
- For each card in order: loads `Company`; generates token via `userService.generateToken`; **`applyAvailableCompanyCreditBalance(paymentRequest.services_availed, companyId, partner ? "manage_service" : "main")`**; builds `oneOffCodes` from resulting line items; creates **`PaymentToken`** (VALID, `valid_until` +1 day).
- Builds **`paymentAllTypes`** payload mimicking controller context: `body` with `card_id`, `payment_token`, `companyId`, `requestPaymentId`, `requestPaymentItems` / `oneOffCodes`, `invoice_tag: "payment_request - " + id`; `user`; `query.companyId` / `oneOffCodes`; `clientTypeConfigName`.
- On **`paymentResult.status === 200`**: sets `paymentRequest.status = USED`, `save()`, pushes to success array, **breaks** card loop (first success wins). Logs failures per card without throwing out of the batch.

### Credits — `controllers-v2/handlers/payment-requests/details.js`

- **`applyAvailableCompanyCreditBalance`**: Wallet balances by currency pool (accounting, corpsec, general); allocates credits against request line totals; appends negative one-off lines using Xero item codes from `getOneOffItemsFromXero` / `xeroCreditBalanceCodes` (e.g. `AC-53-OT-12`, `CO-58-OT-12`, `CO-59-OT-12`).

### Payment execution — `services/payment-all-types.service.js`

- **`paymentAllTypes`**: Validates and consumes `payment_token` (VALID → IN_PROGRESS), validates body (`card_id`, `companyId`, optional `requestPaymentItems` / `requestPaymentId`), then runs the shared invoice + Stripe charge path used elsewhere for card checkout (subscriptions, one-offs, payment-request lines).

### Scheduled execution — `scripts/autoChargePaymentRequests.js`

- Connects Mongo with env/config, calls **`chargePaymentRequests()`**, `process.exit()` — intended for **cron or one-off CLI** runs with the same business rules as the HTTP trigger.

### Schemas (Mongo)

- `schemas/payment-request.js` → **paymentrequests**; `User`, `Company`, `CreditCard`, `PaymentToken` as referenced in service.
