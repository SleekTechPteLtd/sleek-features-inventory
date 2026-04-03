# Find users and profiles for operations support

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Find users and profiles for operations support |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (authenticated admin API; `users` `read` or `full`, `companies` `read`, or `access_management` `read` depending on route — see Evidence) |
| **Business Outcome** | Support and operations staff can locate accounts by group, company, email, or identifiers; see who has elevated or staff roles; load full profiles; and check whether a user has saved payment cards — so investigations and access decisions are grounded in current data. |
| **Entry Point / Surface** | Sleek Admin — authenticated HTTP API on sleek-back: `GET /admin/users/admins`, `GET /admin/companies/:companyId/users`, `GET /admin/users` (elevated list), `GET /admin/staff-users`, `GET /admin/users/:userId`, `POST /admin/users/get-list-info-by-ids`, `GET /admin/users/user-details-from-email/:email`, `GET /admin/users/:userId/has-credit-card`. Exact admin UI labels and navigation are not defined in the referenced files. |
| **Short Description** | Resolves a group via id, name, or identifier (`getGroupByQuery`) and lists members with pagination; searches company-linked users by name; lists all non–“Sleek User” elevated members; lists users holding given resource-allocation role types; fetches a single user by id (optional field projection and auth_token handling); bulk-loads by ids; looks up by email; returns a boolean for stored credit cards. Responses use `sanitizeUserData` unless noted. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Auth**: `userService.authMiddleware` (Auth0, admin SSO, sleek-auth, M2M paths per `user-service`). **RBAC**: `accessControlService.can` / `accessControlMiddleware` on resource and action. **Groups**: `group-service.getGroupByQuery` for admin-by-group listing; `User.findByGroupName` (schema static) for elevated-user sweep. **Related**: `GET /admin/users/me` (own profile) is a separate capability; token-impersonation and group-membership mutation routes in the same controller are out of scope for this inventory row. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `users`; `groups`; `companyusers` (with `user` populated for company name search); `companyresourceusers`; `resourceallocationroles`; `companies` (via aggregation lookups); `creditcards` (existence check for `user`). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether elevated-user listing scales acceptably as group count grows (nested `User.findByGroupName` per group). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/admin/user-controller.js`

- **`GET /admin/users/admins`** — `userService.authMiddleware`, `accessControlMiddleware("access_management", "read")`. Query: optional `group_id`, `group_name`, `identifier` (at least one required); `getGroupByQuery` from `group-service`; rejects missing group, blocks group name `"Sleek User"`. `User.countDocuments` / `User.find` with `{ groups: group._id }`, pagination via `paginationUtil.paginate`, optional `include_pagination_metadata=true`. Maps `userService.sanitizeUserData`.

- **`GET /admin/companies/:companyId/users`** — `authMiddleware` (twice in chain), `accessControlService.can("companies", "read")`. Query `name` (required): regex match on populated users’ `first_name`, `last_name`, `email` via `CompanyUser.find({ company }).populate("user")`.

- **`GET /admin/users`** — `authMiddleware`, `can("users", "read")`. If `get_elevated_users=true`: `Group.find({ name: { $not: /Sleek User/ } })`, then for each group `User.findByGroupName(group.name)`, attach `groupName`, `uniqBy` on `user.id`, return JSON.

- **`GET /admin/staff-users`** — `authMiddleware`, `can("users", "read")`. Query `types` (comma-separated, required): `ResourceAllocationRole.find({ type: { $in: roleTypes } })`, `CompanyResourceUser.find({ resource_role: { $in: roleIds } }).populate("user")`, sanitize and `uniqBy` users by `id`.

- **`GET /admin/users/:userId`** — `authMiddleware`, `can("users", "read")`. Validates ObjectId; optional `fields` query (comma-separated); may select `+auth_token` and mint token if missing; response `sanitizeUserData(user, !includeAuthToken)`.

- **`POST /admin/users/get-list-info-by-ids`** — `authMiddleware`, `can("users", "read")`. Body `user_ids` array → `User.find({ _id: { $in } })`, map `sanitizeUserData`.

- **`GET /admin/users/user-details-from-email/:email`** — `authMiddleware`, `can("users", "read")`. `User.findOne({ email })`, `{ user: sanitizeUserData(user) }`.

- **`GET /admin/users/:userId/has-credit-card`** — `authMiddleware`, `can("users", "full")`. `CreditCard.find({ user: userId })` → `{ hasCreditCard: boolean }`.

- **Also in file (related data, not primary “search”)** — `GET /admin/user/:userId/resource-allocation-role/...` aggregations on `companyresourceusers` with lookups to `users` and `companies`; `GET /admin/users/:userId/referral-code` via `Coupon`; KYC detail routes — omitted from master sheet row but same controller.

### `services/user-service.js`

- **`authMiddleware`** — Resolves user from `Authorization` (Auth0 JWT, admin SSO JWT, sleek-auth, or legacy token / M2M); optional Redis cache `user:<id>`; attaches `req.user`. All listed admin user routes depend on this.

- **`sanitizeUserData(userData, excludeAuthToken = true)`** — Masks `password`, `auth_token` (unless second arg false), `registration_token`, `my_info_sg`; uses `email` or `temporary_email`; `formatUserDataName`. Used for most list/detail responses above.

### `services/group-service.js`

- **`getGroupByQuery(query)`** — If `group_id`: `Group.findById`; `group_name`: `Group.findOne({ name })`; `identifier`: `Group.findOne({ identifier })`. Powers `/admin/users/admins` group resolution.

### `schemas/user.js`

- **`findByGroupName(groupName)`** — Finds `Group` by name, then `User.find({ groups: group })`. Used for elevated-user listing.
