# Manage user group membership

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage user group membership |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (authenticated admin with `access_management` `full`) |
| **Business Outcome** | Staff can add or remove users from admin groups so elevated access and downstream systems (RBAC, optional Camunda) stay aligned with who should operate internal tools and workflows. |
| **Entry Point / Surface** | Sleek Admin — authenticated HTTP API on sleek-back: `PUT /admin/users/add-to-group`, `PUT /admin/users/:userId/remove-from-group`. Exact admin UI labels and navigation are not defined in the referenced files. |
| **Short Description** | Adds a user to a group by email and `group_id` (Mongo `users.groups`), syncs group membership to sleek-auth RBAC for `@sleek.com` users, and optionally registers the user in Camunda when the `camunda_workflow` admin feature flag allows auto-registration for that group name. Removing a user strips the group, calls RBAC remove, audits the action, clears document auto-signing consent, unassigns company resource roles when the user would retain only one group (baseline “Sleek User”), and invalidates Redis user cache in both flows. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Auth**: `userService.authMiddleware`. **RBAC**: `rbacService` → `AuthProxy` (sleek-auth) `addUserToGroup` / `removeUserFromGroup` with `country_code`. **Camunda pilot**: `registerDefaultCamundaUser` → HTTP `POST .../camunda/create-default-user` when CMS `camunda_workflow` / `camunda_user_maintenance` enables the group name in `auto_register_by_group_names`. **Audit**: `auditorService.saveAuditLog` (remove path; resource-role unassignment logs when applicable). **Consent**: `documentSigningConsentService.deleteDocumentAutoSigningConsent` on remove. **Cache**: Redis `user:<id>` via `invalidateUserCacheByUserId`. |
| **Service / Repository** | sleek-back; external: sleek-auth (RBAC proxy), Camunda pilot API |
| **DB - Collections** | `users` (`groups` array updated); `groups` (lookup by id); `companyresourceusers` (read/remove when post-removal `user.groups.length <= 1`). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether non–`@sleek.com` users are expected to receive RBAC sync elsewhere (code skips RBAC API when email is not `@sleek.com`). Which Mongo collections `documentSigningConsentService.deleteDocumentAutoSigningConsent` and auditor persistence write to — not enumerated in the cited files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/admin/user-controller.js`

- **`PUT /admin/users/add-to-group`** — `userService.authMiddleware`, `accessControlService.can("access_management", "full")`. Body: `email`, `group_id` (required). `Group.findById`; resolves `client_type` (`MS_CLIENT` for group name `"MS Partners"`, else `SLEEK_CLIENT`). `User.findOne({ email, client_type })`; `user.groups = user.groups.concat(group._id)`.

- **RBAC on add** — `rbacService.addUserToGroup({ email, group_name: group.name, group_slug: group.group_slug })` after Mongo update (see `rbac-service.js` for `@sleek.com` guard).

- **Camunda on add** — `appFeatureUtil.getAppFeaturesByName("camunda_workflow", "admin")`, `getAppFeatureProp(..., 'camunda_user_maintenance')`; if enabled and `value.auto_register_by_group_names` includes `groupName.toLowerCase()`, `camundaService.registerDefaultCamundaUser({ firstName, lastName, email })`.

- **Cache on add** — `await userService.invalidateUserCacheByUserId(user._id.toString())` before `user.save()` return path (invalidation awaits, then `user.save()` in chain).

- **`PUT /admin/users/:userId/remove-from-group`** — Same auth as add. Body: `group_id`. `Group.findById`, `User.findById(req.params.userId)`; `user.groups` filtered to drop matching group id; `user.save()`.

- **RBAC on remove** — `rbacService.removeUserFromGroup({ email, group_name, group_slug })`.

- **When `user.groups.length <= 1` after save** — `CompanyResourceUser.find({ user }).populate(...)`; each `companyResourceUser.remove` with success/failure audit via `auditorService.saveAuditLog` and `buildAuditLog` (resource role unassignment messaging).

- **Audit on remove** — `buildAuditLog` with synthetic company `{ _id, name, uen: "N/A" }`, action `"removed user from admin groups"`, comment naming remover and removed user.

- **Post-remove** — `documentSigningConsentService.deleteDocumentAutoSigningConsent([user._id])`, `userService.invalidateUserCacheByUserId(user._id.toString())`, JSON response with user.

### `services/user-service.js`

- **`invalidateUserCacheByUserId(userId)`** — Deletes Redis key `user:<userId>` via `deleteRedisCache` (used after add and remove so auth/cache sees updated group membership).

### `modules/sleek-auth/services/rbac-service.js`

- **`addUserToGroup` / `removeUserFromGroup`** — No-op (returns without calling proxy) unless `isValidSleekEmail(email)` (`@sleek.com`). Otherwise `AuthProxy` `addUserToGroup` / `removeUserFromGroup` with `email`, `group_name`, `group_slug`, `country_code` from `get-country-code`.

### `controllers-v2/handlers/camunda-workflow/all.js`

- **`registerDefaultCamundaUser(userBody)`** — `POST` `${config.sleekCamundaPilotBaseApiUrl}/camunda/create-default-user` with `userBody` (firstName, lastName, email from controller).
