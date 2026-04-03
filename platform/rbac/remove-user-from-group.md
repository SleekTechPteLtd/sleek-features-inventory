# Remove user from group

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | Remove user from group |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | M2M-authenticated client (service-to-service) |
| **Business Outcome** | Lets trusted backends remove a user from a tenant-scoped JumpCloud user group by email so directory membership matches RBAC when access is revoked or roles change. |
| **Entry Point / Surface** | `DELETE /rbac/groups/user` — `sleek-auth` RBAC API; protected by `M2MAuthGuard` (Swagger: `@ApiSecurity('basic')`) |
| **Short Description** | Resolves or creates the JumpCloud user group for the given tenant, name, and slug (same serialization as add/sync), then removes the user identified by email from that group via JumpCloud `manageUserGroupMembers` REMOVE. Throws `UserNotFoundError` if the email does not resolve to a JumpCloud user. |
| **Variants / Markets** | SG, HK, AU, UK (tenant via `country_code` / `TENANT` enum on the request body) |
| **Dependencies / Related Flows** | JumpCloud Directory API (`JumpCloudService.getOrCreateUserGroupByName`, `removeUserFromUserGroupByEmail` → `manageUserGroupMembers` REMOVE); inverse `POST /rbac/groups/user` (`addUserToGroup` — `platform/rbac/add-user-to-group.md`); bulk alignment via `syncGroupMembers` CLI (`platform/rbac-sync-user-group-members/sync-user-group-membership-to-jumpcloud.md`) |
| **Service / Repository** | `sleek-auth` — `src/modules/rbac/rbac.controller.ts`, `src/modules/rbac/rbac.service.ts`; `src/modules/jumpcloud/jumpcloud.service.ts` |
| **DB - Collections** | N/A (JumpCloud HTTP API only; no MongoDB in this path) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `getOrCreateUserGroupByName` runs on remove: if the serialized group did not exist in JumpCloud, the service creates it before attempting removal—confirm whether callers rely on this or expect a no-op when the group is absent. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `rbac.controller.ts`

- `@Controller('rbac')`; `removeUserFromGroup`: `@Delete('/groups/user')`, `@UseGuards(new M2MAuthGuard())`, `@ApiSecurity('basic')`.
- `@ApiOperation`: summary “Remove user from a group”, description “This API will remove user from a user group if user is a member”.
- Body: `RemoveUserFromGroupDto`; handler calls `rbacService.removeUserFromGroup(dto)` then `res.status(200).json({ message: 'User Removed' })`.

### `rbac.service.ts` — `removeUserFromGroup`

- `jumpcloudService.getOrCreateUserGroupByName({ name: dto.group_name, slug: dto.group_slug, tenant: dto.country_code })`.
- `jumpcloudService.removeUserFromUserGroupByEmail(dto.email, userGroup.id)`.

### `dto/remove-user-from-group.dto.ts`

- Fields: `country_code` (`TENANT` enum), `email`, `group_name`, `group_slug`.

### `jumpcloud.service.ts` — `removeUserFromUserGroupByEmail`

- `getUserByEmail(email)` (throws `UserNotFoundError` if missing); `proxy.manageUserGroupMembers` with `operation: MANAGE_OPERATION.REMOVE`, `type: ASSOCIATION_TYPE.USER`, user `_id`.

### `jumpcloud.service.ts` — `getOrCreateUserGroupByName`

- Shared with add/sync: serializes group name with env and tenant; finds by name or creates static user group with tenant/slug attributes.
