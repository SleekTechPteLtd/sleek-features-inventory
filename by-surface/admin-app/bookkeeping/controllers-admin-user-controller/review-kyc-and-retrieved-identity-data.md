# Review KYC and retrieved identity data

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Review KYC and retrieved identity data |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Sleek Admin) |
| **Business Outcome** | Internal operations can inspect government- or partner-retrieved identity payloads and Onfido-derived field updates for a user, with change attribution, to support compliance review and verification decisions. |
| **Entry Point / Surface** | Sleek Admin API: `GET /admin/user/{userId}/retrieved-info-details`, `GET /admin/user/{userId}/kyc-onfido-details` (optional query `isGetLastUpdatedOnfidoFields` for the latter). OpenAPI: `public/api-docs/user.yml` documents `kyc-onfido-details`. Exact admin UI navigation not defined in backend code. |
| **Short Description** | Loads a user by `userId` and returns either (1) structured `retrieved_info` with per-field values, `update_origin`, `updated_at`, and resolving `updated_by` to operator names, including nested address keys, or (2) Onfido KYC field update objects from `kyc_onfido.updated_data`, or from `last_updated_onfido_fields` when the query flag is set, each merged with `updated_by` user summary. Read-only; no writes. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Upstream: MyInfo / retrieved-info ingestion (`utils/sleek-my-info-utils.js`, `constants/user-retrieved-info-constants`), Onfido pipeline (`kyc-onfido/`, webhooks, `services/user-service.js` logging of `updated_data` for Onfido). Related review: `POST /v2/company-users/kyc-activity/{userId}` (chronological KYC activity). Onfido applicant/check APIs under `/v2/identity-verification/*`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `users` — fields `retrieved_info` (schema `user-retrieved-info`), `kyc_onfido` (embedded `updated_data` per `schemas/user-onfido-kyc.js`), `last_updated_onfido_fields`; reads also query `users` for `updated_by` display names. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Both routes use `userService.authMiddleware` only (no `accessControlMiddleware` resource check in-controller). Confirm whether API gateway, route registration, or UI restricts these to Sleek Admin / ops roles only. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### HTTP surface

- `controllers/admin/user-controller.js`:
  - `GET /admin/user/:userId/retrieved-info-details` — `userService.authMiddleware`. Reads `User.findById(userId)`; if `retrieved_info` exists, walks `retrieved_info.data` keys; for `address`, expands nested keys under `data.value`; for other keys, returns `value`, `updated_by` (resolved via `User.findById`), `updated_at`, `update_origin`. Default shell `{ address: {} }` when data present.
  - `GET /admin/user/:userId/kyc-onfido-details` — `userService.authMiddleware`. Reads user; `updatedData` from `kyc_onfido.updated_data` unless `req.query.isGetLastUpdatedOnfidoFields` is truthy, then `last_updated_onfido_fields`. For each key in `updatedData`, response entry spreads stored field data and adds `updated_by` (User lookup by `data.updated_by`).

### Schema

- `schemas/user.js`: `retrieved_info` → `retrievedInfoModel.schema`; `kyc_onfido` → `userOnfidoModel.schema`; top-level `last_updated_onfido_fields: Object`.
- `schemas/user-onfido-kyc.js`: `updated_data: Object` on the Onfido subdocument (alongside applicant, documents, checks, reports, extracted_* blobs).

### API docs

- `public/api-docs/user.yml`: path `/admin/user/{userId}/kyc-onfido-details`, tags `user`, `admin`, summary “Get user info that update extracted onfido fields”.

### Tests

- `tests/controllers/user-controller/get-kyc-onfido-details.js` — `GET /admin/user/:userId/kyc-onfido-details/`.
- `tests/controllers/user-controller/get-user-retrieved-data.js` — `GET /admin/user/:userId/retrieved-info-details/`.
