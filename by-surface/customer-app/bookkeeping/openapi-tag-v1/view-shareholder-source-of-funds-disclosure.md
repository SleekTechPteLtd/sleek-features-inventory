# View shareholder source of funds disclosure

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | View shareholder source of funds disclosure |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Compliance, Operations User, Finance User (any caller holding a valid Sleek auth token per route wiring) |
| **Business Outcome** | Authorized parties can retrieve a human-readable HTML summary of a user’s declared shareholder source of funds to support AML and compliance review. |
| **Entry Point / Surface** | `sleek-back` legacy HTTP API: `GET /users/{userId}/source-of-funds` (OpenAPI `public/api-docs/user.yml`, tags `user` and `v1`, `sleek_auth` security). Mounted via `app-router.js` glob load of `controllers/**/*.js` (not under `/v2/...`). Exact Sleek app or Admin UI path is not defined in these files. |
| **Short Description** | Loads the `User` by `userId`, reads `shareholder_source_of_fund`, and returns JSON `{ html }` where `html` is a full HTML document string listing each declared source (with optional `otherSourceOfFunds` / `otherReasonForIncorporation` text-value pairing). If no entries exist, `createHtmlFromList` yields a non-string value that serializes to an empty object for `html` in practice (see tests). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Write path**: user profile update routes in `user-controller.js` accept `shareholder_source_of_fund` arrays and persist to the same user field. **Related data**: company-level `sourceOfFunds` on `Company` (e.g. onboarding / questionnaires) is separate from per-user `shareholder_source_of_fund`. **Rendering**: `userService.createHtmlFromList` shared pattern with questionnaire HTML helpers that also format company `sourceOfFunds` lists (`controllers-v2/handlers/pre-payment-questionnaire-view/pre-payment-questionnaire.js`). |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `users` (Mongoose model `User`; field `shareholder_source_of_fund`), read-only for this GET handler. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | The GET handler only applies `userService.authMiddleware` and does not call `canManageUserMiddleware` or similar; whether production access is restricted by another layer (BFF, gateway, or client-only use) is not visible here. Empty SOF behavior relies on JSON serialization of a returned `Error` from `createHtmlFromList` (tests expect `{ html: {} }`). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/user-controller.js`

- **`GET /users/:userId/source-of-funds`**: `userService.authMiddleware` → `User.findOne({ _id: params.userId })`. Missing user → `422` with `ERROR_CODES.USERS.SOURCE_OF_FUNDS_USER_NOT_FOUND`. Success → `res.json({ html: userService.createHtmlFromList(user.shareholder_source_of_fund) })`. Catch → `500` with `tenant.general.messages.errors.USERS.INVALID_SOURCE_OF_FUNDS_API_ERROR` (includes invalid `userId` shape).

### `services/user-service.js`

- **`createHtmlFromList(list)`**: Builds HTML with title “Source of Funds” and ordered list items; each item uses `data.text`, or `` `${data.text} - ${data.value}` `` when `data.type` is `otherSourceOfFunds` or `otherReasonForIncorporation`. If `list` is empty or missing, returns `new Error("No Source of Funds saved")` (not a string).

### `schemas/user.js`

- **`shareholder_source_of_fund`**: Array of subdocuments `{ text, type, value }` (strings).

### `public/api-docs/user.yml`

- **`/users/{userId}/source-of-funds`**: `get`, tags `user` and `v1`, `sleek_auth`, summary describes generated HTML from user SOF data; response `200` with `html` (documented as string).

### Tests

- `tests/controllers/user-controller/source-of-funds.js` — `200` with `{ html: {} }` when no SOF; `200` with HTML string containing saved text when SOF present; `401` without token; `422` for missing user; `500` for invalid ObjectId.
