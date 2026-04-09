# Issue short-lived payment tokens

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Issue short-lived payment tokens |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Authenticated user (any role that can call the mint endpoint before a payment or billing action) |
| **Business Outcome** | Users obtain a server-recognized credential they can attach to payment and billing requests so those operations can be validated, de-duplicated while in flight, and tied to a defined token lifecycle (valid → in progress → terminal states). |
| **Entry Point / Surface** | Sleek API: `POST /v2/payment-tokens/create` (mounted in `app-router.js` under `/v2/payment-tokens`). Exact in-app screen or flow name is not defined in these files. |
| **Short Description** | After session authentication, the service generates a UUID token, persists it as `valid` with a one-day expiry, and returns it to the client. Downstream payment and billing handlers accept `payment_token` in the body, look up the row, enforce status transitions (for example `valid` → `in_progress`), and remove or update the token when the operation completes. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Consumption: legacy `controllers/payment-controller.js` and `services/payment-all-types.service.js` (validate and update token status around charges); v2 billing: `controllers-v2/handlers/billing-payment/payment-util.js` (`checkPaymentToken`), `unpaid-bills.js`, `corp-sec-subscription.js`; system-issued tokens also created in `services/auto-charge-payment-request-service.js`, `controllers/admin/payment-request-controller.js`, and operational scripts (renewals, fees). Token values are produced with `userService.generateToken()` at mint time. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `paymenttokens` (Mongoose model `PaymentToken`; fields `payment_token`, `status`, `valid_until`, timestamps) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether product intends user-scoped tokens: the create handler logs `req.user._id` but does not persist a user reference on `PaymentToken`, so correlation is by token string only. Whether clients rely on `valid_until` for rejection is not enforced in `payment-util.checkPaymentToken` (status-only checks in that path). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Mint (authenticated user)

- `app-router.js`: `router.use("/v2/payment-tokens", require("./controllers-v2/payment-token"))`.
- `controllers-v2/payment-token.js`: `POST /create` → `userService.authMiddleware`, handler `createPaymentToken.create`.
- `controllers-v2/handlers/payment-token/create.js`: `userService.generateToken()`; `PaymentToken.create({ payment_token, status: PAYMENT_TOKEN_STATUSES.VALID, valid_until: moment().add(1, 'days') })`; responds `200` with `{ payment_token }`; errors → `500` via `errorHandler.default_error_500()`.

### Schema and statuses

- `schemas/payment-token.js`: Mongoose schema `payment_token` (string), `status` (string), `valid_until` (date), `timestamps: true`; model name `PaymentToken`.
- `constants/payment-token-statuses.js`: `VALID` (`"valid"`), `IN_PROGRESS` (`"in_progress"`), `USED_PAYMENT_FAILED` (`"used_payment_failed"`).

### Downstream validation (representative)

- `controllers-v2/handlers/billing-payment/payment-util.js`: `checkPaymentToken` — `findOne` by `payment_token`; if `VALID`, `updateOne` to `IN_PROGRESS` and return success; if already `IN_PROGRESS`, respond with `PAYMENT_TOKEN_BEING_PROCESSED`; missing/invalid → `PAYMENT_TOKEN_NOT_EXISTING` or validation error if `payment_token` omitted.
- `controllers/payment-controller.js` and `services/payment-all-types.service.js`: parallel patterns for token lookup, status updates, `deleteMany` / `updateOne` after payment outcomes (broader payment flows; same collection).
