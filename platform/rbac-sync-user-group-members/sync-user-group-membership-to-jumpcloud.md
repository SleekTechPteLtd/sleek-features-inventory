# Sync user group membership to JumpCloud

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | Sync user group membership to JumpCloud |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | The platform reconciles Sleek-backed group membership into JumpCloud so users land in the correct identity groups for SSO and application access. |
| **Entry Point / Surface** | `sleek-auth` NestJS CLI: `rbac:sync:user-group-members <tenant>` (`TENANT`: `SGP`, `HKG`, `AUS`, `GBR`) — not an end-user HTTP route |
| **Short Description** | For each non-default group from the Sleek Back repository client, loads members (excluding non-Sleek users), ensures a matching JumpCloud user group exists and is bound to the configured JumpCloud application, then adds each member to that group by email. |
| **Variants / Markets** | SG, HK, AU, UK (via `TENANT` passed to the command) |
| **Dependencies / Related Flows** | Sleek Back HTTP API (groups and group members via `SleekBackProxy`); JumpCloud Directory API; sibling CLI `rbac:sync:user-groups` (groups and app association only, no members); ad hoc `RbacService.addUserToGroup` / `removeUserFromGroup` |
| **Service / Repository** | `sleek-auth` — `src/modules/rbac/rbac.service.ts` (`syncGroupMembers`), `src/modules/rbac/rbac.command.ts`, `src/modules/rbac/repository-clients/sleek-back.client.ts` (`getGroups`); `src/modules/user/user.service.ts` (`getUsersByGroupId` → `src/modules/user/repository-clients/sleek-back.client.ts`); `src/modules/jumpcloud/jumpcloud.service.ts` |
| **DB - Collections** | N/A (Sleek Back and JumpCloud HTTP APIs only; no MongoDB in this path) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/modules/rbac/rbac.command.ts`

- `rbac:sync:user-group-members` → `this.rbacService.syncGroupMembers(tenant)`; positional `tenant`; exits `0` / `1`.

### `src/modules/rbac/rbac.service.ts` — `syncGroupMembers`

- `getRepositoryClient(tenant)` → `SleekBackClient` when `repository_client` is `SLEEK_BACK`.
- `repository.getGroups()`; per group: `userService.getUsersByGroupId({ group_id: group._id, tenant, exclude_non_sleek_user: true })`; skips empty groups.
- `jumpcloudService.getOrCreateUserGroupByName` (`group.name`, `group.group_slug`, `tenant`); `assignUserGroupToApplication`, then per member `assignUserToUserGroupByEmail(member.email, userGroup.id)` with try/catch logging.

### `src/modules/rbac/repository-clients/sleek-back.client.ts` — `getGroups`

- Paginates `clientProxy.getGroups` with `exclude_default_group: true`, `limit` 20.

### `src/modules/user/user.service.ts` — `getUsersByGroupId`

- Delegates to `SleekBackClient.getUsersByGroupId` for the tenant’s repository client (implementation in `src/modules/user/repository-clients/sleek-back.client.ts` — `getGroupMembers` pagination).

### `src/modules/jumpcloud/jumpcloud.service.ts`

- `getOrCreateUserGroupByName`: serialized name (`Admin Platform`, `NODE_ENV`, tenant, group label); create with static membership and `attributes.group` `{tenant}.{slug}`.
- `assignUserGroupToApplication`: `manageApplicationAssociation` ADD `USER_GROUP` to `jumpcloud.application_id`.
- `assignUserToUserGroupByEmail`: resolve user by email, `manageUserGroupMembers` ADD.
