# Inspect receipt user profiles for internal operations

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Inspect receipt user profiles for internal operations |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (internal services: Basic-auth client id/secret against configured internal secret; not end-user or browser clients per middleware warning) |
| **Business Outcome** | Support and integrations can list Sleek Receipts user records with optional company and date filters so receipt-user state can be inspected or reconciled across companies without exposing this surface to public clients. |
| **Entry Point / Surface** | Internal HTTP API on sleek-back: `GET /internal/receipt-users` (query: optional `company_id`, `start_date`, `end_date`, `skip`, `limit`). Not a Sleek App or Admin UI route in the referenced files. |
| **Short Description** | Returns paginated `ReceiptUser` documents filtered by company and/or an `updatedAt` date range (`start_date`/`end_date`, inclusive start/end of day). Default pagination `skip=0`, `limit=10`. Response shape: `{ status_code, message, data }`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Auth**: `internalServicesMiddleware()` — Basic `Authorization` with base64 `clientId:clientSecret`, validated via `internal-service` secret (optional bypass in non-prod). **Data**: `ReceiptUser` Mongoose model; `company` ObjectId ref to `Company`. **Related**: Sleek Receipts user lifecycle (status, access levels, phone verification) as modeled on `ReceiptUser`; admin UI column visibility tied to `shared-data` `access_levels_settings` per schema comment (out of scope for this route). |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `receiptusers` |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether consumers rely on `updatedAt` as “activity” or need a different date field; whether `limit` cap should be enforced for large tenants. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/internal-service/receipt-user-controller.js`

- **`GET /internal/receipt-users`** — `internalServicesMiddleware()`. Query validation (Joi-style via `Validator.object`): optional `company_id` (string), `start_date`, `end_date` (strings), `skip`, `limit` (numbers). Builds Mongo query: if both `start_date` and `end_date`, adds `updatedAt: { $gte: moment(start_date).startOf('day'), $lte: moment(end_date).endOf('day') }`; if `company_id`, adds `company: company_id`. `ReceiptUser.find(queryParams).skip(skip).limit(limit)`. Returns JSON `status_code: 200`, `data: receiptUsers`.

### `schemas/receipt-user.js`

- **Model** — `mongoose.model("ReceiptUser", receiptUserSchema)` → collection **`receiptusers`** (default Mongoose pluralization).

- **Fields (context for listed documents)** — `first_name`, `last_name`, `company` (ref Company), `emails`, `email_in_address` (unique sparse index), `phone_numbers`, `receipt_bank_address`, `status` (ACTIVE/INACTIVE/ARCHIVED), `activation_code`, `access_levels` (company_receipts, expense_claims, approve_expense_claims), `phone_numbers_v2`, `status_v2` (SLEEK_TO_ACTIVATE / ENABLED / DISABLED / ARCHIVED), `timestamps` → `createdAt` / `updatedAt`.

### `middlewares/internal-services.js`

- **`internalServicesMiddleware()`** — Internal server-to-server auth: optional bypass via `internalService.bypassAuth()`; else requires `Authorization: Basic <base64(clientId:clientSecret)>` matching `internalService.getSecretToken()`; sets `req.clientId` and request tracer client id. Comments warn against use from web clients.
