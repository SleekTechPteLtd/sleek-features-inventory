# Manage promotional coupons

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage promotional coupons |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (admin API with `coupons` permission: `full` for create/update/delete, `read` for search/list) |
| **Business Outcome** | Operations can define and maintain discount codes (amount, validity, usage limits, which services they apply to) so promotions are applied in a controlled way and kept separate from referral-program coupons in admin search. |
| **Entry Point / Surface** | Authenticated admin HTTP API on sleek-back: `POST /admin/coupons`, `PUT /admin/coupons/:couponId`, `DELETE /admin/coupons/:couponId`, `GET /admin/coupons` (`accessControlService.can("coupons", "full")` or `can("coupons", "read")` as above). Exact Sleek admin UI label for these routes is not defined in the referenced files. |
| **Short Description** | Create coupons with unique codes, negative integer amounts (discount magnitude), optional title and expiry (defaults to one year ahead if omitted), usage cap (`max_usage_nb`, default 1), and `applicable_service`. Update or delete by id with validation (e.g. usage cap not below current usage, code uniqueness). List and filter coupons by code, title, amount, expiry with pagination and sorting; list results exclude `type: referral_program` and omit `bind_to` from the response. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Referral program**: schema supports `type` `default` | `referral_program`; admin listing explicitly filters out `referral_program` so operational “promotional” coupons are shown separately from referral coupons. **Auth**: `userService.authMiddleware` plus RBAC on `coupons`. Redemption and customer-facing application of coupons are not implemented in these two files. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `coupons` (Mongoose model `Coupon`; fields include `code`, `amount`, `title`, `expired_at`, `max_usage_nb`, `current_usage_nb`, `bind_to`, `type`, `applicable_service`, timestamps). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Where redemption increments `current_usage_nb` and enforces limits (not in referenced files). Whether `GET /admin/coupons` should return a total count alongside the page (`countDocuments` appears on the same chain as `find` but is not wired to the response). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/admin/coupon-controller.js`

- **`POST /admin/coupons`** — `userService.authMiddleware`, `accessControlService.can("coupons", "full")`; `validationUtils.validateOrReject` for `code` (string, required), `amount` (integer, required), optional `expired_at`, `title`, `max_usage_nb`, `applicable_service`; rejects non-negative `amount`; defaults `max_usage_nb` to 1; sets `status` to `"new"`, `current_usage_nb` to 0; parses `expired_at` or defaults with `moment().add(1, "year")`; `Coupon.findOne({ code })` then `Coupon.create`.
- **`PUT /admin/coupons/:couponId`** — `can("coupons", "full")`; optional body fields same shape as create; `amount` must remain negative if present; `max_usage_nb` cannot be less than existing `current_usage_nb`; `Coupon.findOne` by id, then code uniqueness excluding self; `Coupon.updateOne({ _id: couponId }, couponData)`.
- **`DELETE /admin/coupons/:couponId`** — `can("coupons", "full")`; `Coupon.deleteOne({ _id: couponId })`.
- **`GET /admin/coupons`** — `can("coupons", "read")`; query filters `code`, `title`, `amount`, `expired_at`; `skip`/`limit` (default limit 50); `sortBy` / `sortOrder` (default `createdAt`, `-1`); optional `select`; `findQuery.type = { $ne: "referral_program" }`; optional case-insensitive regex on `code`/`title` unless `isCaseSensitive=false`; amount filter negated for query (`amount * -1`); response maps coupons with `omit(coupon, ["bind_to"])`. Note: `Coupon.countDocuments(findQuery)` is invoked in the same expression chain as `Coupon.find` but no count is returned in the handler.

### `schemas/coupon.js`

- **Model `Coupon`** — `code` (unique, required), `amount`, `title`, `expired_at`, `max_usage_nb`, `current_usage_nb` (default 0), `bind_to` (array of company/status/user/ref_bonus/used_at), `type` enum `default` | `referral_program` (default `default`), `applicable_service` enum `general` | `accountingPlan` | `corpSec` (default `general`), `timestamps: true`.
