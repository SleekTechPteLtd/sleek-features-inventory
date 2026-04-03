# Check signup email availability

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Check signup email availability |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Prospect (website onboarding) |
| **Business Outcome** | Prospects learn whether an email is already registered for the chosen client type before they continue signup, reducing duplicate accounts and support friction. |
| **Entry Point / Surface** | Sleek marketing website onboarding (incorporation / accounting transfer flows); API `GET /v2/sleek-site-onboarding/check-existing-email` with query `email` and optional `client_type` (defaults to `sleekClient`). |
| **Short Description** | The backend looks up a user document matching the supplied email and `client_type`. It returns `{ isExisting: true }` if a user exists for that combination, otherwise `false`. Email is stored lowercase on the user model; the same email may exist under a different `client_type` without counting as a duplicate for that check. |
| **Variants / Markets** | Unknown — route is not tenant-gated in the controller; behaviour depends on shared DB and deployed tenant. |
| **Dependencies / Related Flows** | User registration and `client_type` model (`sleekClient`, `msClient`, etc.); broader sleek-site-onboarding routes (e.g. cart, save-for-later email) in the same controller. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `users` (User model — `findOne` on `email` and `client_type`). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether the website always passes `client_type` for MS vs Sleek flows; exact OpenAPI coverage for this path (YAML in repo lists other onboarding paths). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/sleek-site-onboarding.js`

- **`GET /check-existing-email`** — No auth middleware on this handler (contrast with `POST /cart-details/` which uses `userService.getUserInfoMiddleWare`).
- **Query** — `email` from `req.query`; `client_type` from `req.query` with default `"sleekClient"` via `lodash/get`.
- **Logic** — `User.findOne({ email, client_type })`; if a document exists, `isExisting` is set to `true`.
- **Response** — JSON `{ isExisting }`; on error, HTTP 422 with `name: "CheckExistingEmailError"`.

### `schemas/user.js`

- **`email`** — String, trimmed, indexed, sparse, **lowercase** via schema (no unique constraint on email alone).
- **`client_type`** — String, default `"sleekClient"`, indexed, sparse; comment in schema notes removal of unique email to allow same email with different client types.

### Mounting

- Router mounted at `/v2/sleek-site-onboarding` in `app-router.js`, so full path is `/v2/sleek-site-onboarding/check-existing-email`.

### Columns marked Unknown

- **Variants / Markets**: No regional branching in the cited handler; tenant behaviour not derived from these files alone.
- **Disposition**: No production analytics in scope for this write.
