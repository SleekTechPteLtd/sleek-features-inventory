# Record admin user profile review

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Record admin user profile review |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations / Admin (users resource, full) |
| **Business Outcome** | Persists whether internal staff have reviewed a user’s profile so onboarding and compliance processes can treat that review as complete or pending. |
| **Entry Point / Surface** | Sleek Admin — `POST /admin/users/:userId/reviewed-by-admin` with body `{ "is_reviewed_by_admin": boolean }` (authenticated admin session). Exact UI navigation path not defined in backend code. |
| **Short Description** | Operators with full permission on the `users` admin resource set the user’s `is_reviewed_by_admin` flag and save the document; the API returns the sanitized user. The flag can be cleared indirectly when new user or company-user flows reset it to `false`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | User and company-user creation/update paths set `is_reviewed_by_admin` to `false` (`controllers/user-controller.js`, `controllers/company-user-controller.js`, `services/invitations/invitation-service.js`). Consumers of the flag for workflow gating may live outside this controller (e.g. app or other services). |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `users` (`User` schema field `is_reviewed_by_admin`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | No other sleek-back services read this flag for automation (only writes/resets and tests); confirm which frontends or workflows gate on `is_reviewed_by_admin`. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### HTTP surface

- `controllers/admin/user-controller.js`: `POST /admin/users/:userId/reviewed-by-admin`
  - Guards: `userService.authMiddleware`, `accessControlService.can("users", "full")` (RBAC: full access on `users` resource).
  - Body validation: `is_reviewed_by_admin` — boolean, required (`validationUtils.validateOrReject`).
  - Handler: `User.findById(req.params.userId)` → assign `user.is_reviewed_by_admin` → `user.save()` → `res.send(userService.sanitizeUserData(user))`.
  - Errors: `422` with validation/other errors via `errorService.notifyReqError` (promise chain).

### Data model

- `schemas/user.js`: `is_reviewed_by_admin: Boolean` under a “Reviewed by admin” comment.
- `swagger.yml` / `public/api-docs`: `User` model documents `is_reviewed_by_admin` as boolean.

### Reset behaviour (downstream of “reviewed” state)

- `controllers/company-user-controller.js` (multiple paths): `companyUserData.user.is_reviewed_by_admin = false` when creating/updating company user payloads.
- `controllers/user-controller.js`: `userData.is_reviewed_by_admin = false` in an update path.
- `services/invitations/invitation-service.js`: sets `companyUserData.user.is_reviewed_by_admin = false` when building company user data.

### Automated tests

- `tests/controllers/user-controller/set-is-reviewed-by-admin.js`: asserts `200` and persisted `true` when the admin has `users: full` on a group; `401` and unchanged flag when the admin lacks that permission.

### Response shaping

- `services/user-service.js`: `sanitizeUserData` strips sensitive fields (`password`, `auth_token` when excluded, etc.) and formats names; it does not remove `is_reviewed_by_admin`, so the flag is visible on the JSON response.
