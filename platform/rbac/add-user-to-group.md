# JumpCloud assign user to group

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | JumpCloud assign user to group |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (M2M-authenticated services, internal restore script) |
| **Business Outcome** | Ensures a user is placed in the correct tenant-scoped JumpCloud user group so directory-backed access and app bindings match Sleek RBAC intent without manual JumpCloud UI work. |
| **Entry Point / Surface** | `POST /rbac/groups/user` — `sleek-auth` RBAC API (`M2MAuthGuard`, Swagger `@ApiSecurity('basic')`); optional bulk path: NestJS command `script:restore-access <tenant>` reading `data/<tenant>-users.json` and calling `addUserToGroup` per user/group |
| **Short Description** | Resolves or creates the JumpCloud user group (serialized name, tenant, slug attributes; static membership) then looks up the user by email in JumpCloud and adds them to that group via `manageUserGroupMembers` ADD. |
| **Variants / Markets** | SG, HK, AU, UK (tenant via `country_code` / `TENANT` on the DTO or CLI positional) |
| **Dependencies / Related Flows** | JumpCloud Directory API (`JumpCloudProxy`); `DELETE /rbac/groups/user` (`removeUserFromGroup`); bulk alignment `syncGroupMembers` CLI (`platform/rbac-sync-user-group-members/sync-user-group-membership-to-jumpcloud.md`) |
| **Service / Repository** | `sleek-auth` — `src/modules/rbac/rbac.controller.ts`, `src/modules/rbac/rbac.service.ts` (`addUserToGroup`); `src/modules/jumpcloud/jumpcloud.service.ts` (`getOrCreateUserGroupByName`, `assignUserToUserGroupByEmail`, `getUserByEmail`); `src/scripts/restore-access.script.ts` |
| **DB - Collections** | N/A (JumpCloud HTTP API only; no MongoDB in this path) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether JumpCloud treats duplicate membership adds as success or error (no local membership check). Handler returns HTTP 201 while `@ApiOkResponse` documents 200—align OpenAPI vs runtime if needed. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `rbac.controller.ts`

- `@Controller('rbac')`; `addUserToGroup`: `@Post('/groups/user')`, `@UseGuards(new M2MAuthGuard())`, `@ApiSecurity('basic')`.
- `@ApiOperation`: summary “Add user to a group”, description “This API will add user to a user group if not already added”.
- Body: `AddUserToGroupDto`; handler calls `rbacService.addUserToGroup(dto)` then `res.status(201).json({ message: 'User Added' })`.

### `rbac.service.ts` — `addUserToGroup`

- `jumpcloudService.getOrCreateUserGroupByName({ name: dto.group_name, slug: dto.group_slug, tenant: dto.country_code })`.
- `jumpcloudService.assignUserToUserGroupByEmail(dto.email, userGroup.id)`.

### `dto/add-user-to-group.dto.ts`

- Fields: `country_code` (`TENANT` enum), `email`, `group_name`, `group_slug`.

### `jumpcloud.service.ts` — `getOrCreateUserGroupByName`

- Builds display name via `serializeUserGroupName` (`Admin Platform`, `NODE_ENV`, tenant, trimmed name); `proxy.getUserGroupByName(serializedUserGroupName)` or `createUserGroup` with `membershipMethod: STATIC`, `attributes.group` = `${tenant}.${slug}`.

### `jumpcloud.service.ts` — `assignUserToUserGroupByEmail`

- `getUserByEmail(email)` (`email:eq:` query; throws `UserNotFoundError` if missing) then `proxy.manageUserGroupMembers` with `operation: MANAGE_OPERATION.ADD`, `type: ASSOCIATION_TYPE.USER`, `id: user._id`.

### `restore-access.script.ts`

- Command `script:restore-access` with positional `tenant`; parses JSON users and per group calls `rbacService.addUserToGroup` with `email`, `group_name`, `group_slug`, `country_code: tenant`.
