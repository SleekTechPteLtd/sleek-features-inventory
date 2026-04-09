# Align payment request date for auto-charge

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Align payment request date for auto-charge |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators can place a new payment request into the calendar window the automated card-charge job uses, so the client is charged on the intended day instead of being skipped or delayed. |
| **Entry Point / Surface** | Authenticated HTTP API: `POST /v2/auto-charge-payment-requests/update-date` (body: `paymentRequestNumber`, `date` as `DD/MM/YYYY`). Related: `POST /v2/auto-charge-payment-requests/trigger-process` runs the auto-charge batch on demand. |
| **Short Description** | For a **NEW** payment request, updates Mongo `createdAt` from a supplied date so it matches the batch rule that selects requests created on the day **two calendar days ago**. A separate endpoint triggers the same charge pipeline that iterates those requests, resolves company cards, and charges via the shared payment-all-types path. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `services/auto-charge-payment-request-service.js` (`getNewPaymentRequests`, `chargePaymentRequests`); `payment-all-types.service`; `credit-card-service`; `user-service` (token generation); `controllers-v2/handlers/payment-requests/details` (`applyAvailableCompanyCreditBalance`); Stripe/card charging via existing payment stack; `User`, `Company`, `CreditCard`, `PaymentToken` documents during charge. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | **Update path:** paymentrequests. **Trigger/charge path (same module):** paymentrequests, users, companies, creditcards, paymenttokens |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether a first-party UI calls these routes or they are ops-only/API; whether all tenants share the “two days ago” window; `updateCreatedDate` log line says “Updating status” but mutates `createdAt` only. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Router — `app-router.js`

- Mounts `controllers-v2/auto-charge-payment-requests` at **`/v2/auto-charge-payment-requests`**.

### Controllers — `controllers-v2/auto-charge-payment-requests.js`

- **`POST /update-date`** (`userService.authMiddleware`): `updateCreatedDate`.
- **`POST /trigger-process`** (`userService.authMiddleware`): `triggerAutoChargePaymentRequests`.

### Handlers — `controllers-v2/handlers/payment-requests/auto-charge-payment-requests.js`

- **`updateCreatedDate`**: Requires `paymentRequestNumber` and `date` in body; strips `PR-` prefix; `PaymentRequest.findOne({ number })`; rejects unless `status === NEW` (`PAYMENT_REQUEST_STATUSES.NEW`). Sets `paymentRequest.createdAt` to `moment(date, 'DD/MM/YYYY').format('YYYY-MM-DD hh:mm')`, `save()`, returns document.
- **`triggerAutoChargePaymentRequests`**: Calls `chargePaymentRequests()` from `services/auto-charge-payment-request-service`, returns `{ payment_requests: [...] }`.

### Service — `services/auto-charge-payment-request-service.js`

- **`getNewPaymentRequests`**: `PaymentRequest.find` with `status: NEW` and `createdAt` between **start and end of the calendar day that is `moment().add(-2, 'day')`** (i.e. “two days ago” in server local time). Cursor for batch processing.
- **`chargePaymentRequests`**: For each matching PR, loads user by email, eligible `CreditCard`s for the company, applies company credit via `applyAvailableCompanyCreditBalance`, creates a `PaymentToken`, builds payload for `paymentAllTypes`, on HTTP 200 sets PR status to `USED` and records success.

### Schema — `schemas/payment-request.js`

- Mongoose model **`PaymentRequest`** with `timestamps: true` (so `createdAt`/`updatedAt`); fields include `company`, `to_be_paid_by`, `status`, `services_availed`, `number` via `mongoose-sequence` auto-increment, etc. Collection name follows Mongoose default for model name `PaymentRequest` (typically **paymentrequests**).
