# Manage user group membership

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | Manage user group membership |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | M2M-authenticated services (machine callers); optional internal scripts using the same service methods |
| **Business Outcome** | Keeps JumpCloud user group membership aligned with Sleek tenant RBAC definitions when trusted backends add or remove users, so directory-backed identity and application access stay consistent without manual JumpCloud administration. |
| **Entry Point / Surface** | `POST /rbac/groups/user` and `DELETE /rbac/groups/user` — `sleek-auth` RBAC API (`M2MAuthGuard`, Swagger `@ApiSecurity('basic')`); related granular docs: `platform/rbac/add-user-to-group.md`, `platform/rbac/remove-user-from-group.md` |
| **Short Description** | M2M callers supply tenant (`country_code`), user email, and Sleek group name/slug. The service resolves or creates the tenant-scoped JumpCloud user group (serialized name and attributes), then adds or removes the JumpCloud user (by email lookup) via `manageUserGroupMembers` ADD or REMOVE. |
| **Variants / Markets** | SG, HK, AU, UK (tenant via `TENANT` / `country_code` on the DTO) |
| **Dependencies / Related Flows** | JumpCloud Directory API via `JumpCloudProxy`; bulk alignment CLIs (`syncGroupMembers`, `syncUserGroups` — see `platform/rbac-sync-user-groups/` and `platform/rbac-sync-user-group-members/`); restore script path in `add-user-to-group` inventory |
| **Service / Repository** | `sleek-auth` — `src/modules/rbac/rbac.controller.ts`, `src/modules/rbac/rbac.service.ts`; `src/modules/jumpcloud/jumpcloud.service.ts`; DTOs `src/modules/rbac/dto/add-user-to-group.dto.ts`, `src/modules/rbac/dto/remove-user-from-group.dto.ts` |
| **DB - Collections** | N/A (JumpCloud HTTP API only; no MongoDB in this API path) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Add handler returns HTTP 201 while `@ApiOkResponse` documents 200—align OpenAPI vs runtime if needed. `getOrCreateUserGroupByName` on remove may create a group that did not exist before removal—confirm caller expectations. Whether JumpCloud treats duplicate membership adds as success or error (no local membership check before add). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `rbac.controller.ts`

- `@Controller('rbac')`; both routes use `@UseGuards(new M2MAuthGuard())`, `@ApiSecurity('basic')`.
- `addUserToGroup`: `@Post('/groups/user')`, body `AddUserToGroupDto`, `rbacService.addUserToGroup(dto)`, response `201` + `{ message: 'User Added' }`. `@ApiOperation` summary “Add user to a group”.
- `removeUserFromGroup`: `@Delete('/groups/user')`, body `RemoveUserFromGroupDto`, `rbacService.removeUserFromGroup(dto)`, response `200` + `{ message: 'User Removed' }`. `@ApiOperation` summary “Remove user from a group”.

### `rbac.service.ts`

- `addUserToGroup`: `jumpcloudService.getOrCreateUserGroupByName({ name: dto.group_name, slug: dto.group_slug, tenant: dto.country_code })` then `assignUserToUserGroupByEmail(dto.email, userGroup.id)`.
- `removeUserFromGroup`: same `getOrCreateUserGroupByName` then `removeUserFromUserGroupByEmail(dto.email, userGroup.id)`.

### `jumpcloud.service.ts`

- `getOrCreateUserGroupByName`: serializes display name (`Admin Platform`, `NODE_ENV`, tenant, name); `getUserGroupByName` or `createUserGroup` with static membership and `attributes.group` = `${tenant}.${slug}`.
- `assignUserToUserGroupByEmail` / `removeUserFromUserGroupByEmail`: `getUserByEmail` (throws `UserNotFoundError` if missing); `proxy.manageUserGroupMembers` with `MANAGE_OPERATION.ADD` or `REMOVE`, `ASSOCIATION_TYPE.USER`.

### DTOs

- Shared shape: `country_code` (`TENANT`), `email`, `group_name`, `group_slug`.
