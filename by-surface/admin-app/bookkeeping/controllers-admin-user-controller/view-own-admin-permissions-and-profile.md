# View own admin permissions and profile

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | View own admin permissions and profile |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | A signed-in admin operator can load their own profile, effective resource permissions, and super-admin classification so the admin console can render the correct UI and enforce client-side checks. |
| **Entry Point / Surface** | Sleek Admin Console — `GET /admin/users/me` (authenticated admin session). Exact UI navigation path not defined in backend code. |
| **Short Description** | After `userService.authMiddleware` resolves the user, the handler loads group membership via `getUserAccess`, computes highest permission per admin resource, `isSuperAdmin` (Super Admin group), and `profile` (Sleek Admin group vs user), and returns the augmented user through `sanitizeUserData`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Depends on admin auth (`authMiddleware`: Auth0 / admin SSO / token paths per `user-service`). Group roles drive RBAC; `getUserAccess` caches by group id list in Redis. Related: other admin routes that use `accessControlMiddleware` / `accessControlService` for per-resource checks. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `groups` (read via `Group.find` for the signed-in user’s groups, with `parent` populated); `users` (read in `authMiddleware` before this handler runs). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether non-admin authenticated users can hit this route (middleware allows any authenticated user path; UI may still gate “admin” only). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### HTTP surface

- `controllers/admin/user-controller.js`: `GET /admin/users/me` — `userService.authMiddleware` only (no `accessControlMiddleware` resource check). Handler: `getUserAccess(req.user.groups)` → `UserAccess` instance; sets `req.user._doc.isSuperAdmin` from `userAccess.isSuperAdmin()`, `req.user._doc.profile` from `userAccess.getProfile()`, `req.user._doc.permissions` from `userAccess.getHighestPermissions()`; responds with `userService.sanitizeUserData(req.user)`.

### Access computation

- `services/get-user-access.js`:
  - `getUserAccess(groupIds)` — Redis cache key `user_access:<sorted group ids>`; on miss, `Group.find({ _id: { $in: groupIds } }).populate("parent")`, caches serialized groups for 15 minutes.
  - `UserAccess.isSuperAdmin()` — `"admin"` if member of group name `"Super Admin"` (including parent group match via `isMember`), else `"user"`.
  - `UserAccess.getProfile()` — `"admin"` if member of `"Sleek Admin"`, else `"user"`.
  - `UserAccess.getHighestPermissions()` — per-resource highest of `full` / `edit` / `read` / `none` from `group.role` and `group.parent.role` (resources include `companies`, `users`, `access_management`, `files`, `invoices`, etc.), used for the `permissions` object on the response payload.

### Response shaping

- `services/user-service.js`: `sanitizeUserData` strips sensitive fields (`password`, `auth_token` by default, `registration_token`, `my_info_sg`) and normalizes display name; the handler adds `isSuperAdmin`, `profile`, and `permissions` onto the user document before sanitization.
