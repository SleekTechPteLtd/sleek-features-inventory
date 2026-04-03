# Sync repository groups to JumpCloud

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | Sync repository groups to JumpCloud |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (scheduled or manual CLI; operations / automation) |
| **Business Outcome** | Ensures every Sleek Back tenant group has a corresponding JumpCloud user group and that each group is associated with the configured JumpCloud application so downstream access and SSO bindings stay aligned. |
| **Entry Point / Surface** | `sleek-auth` NestJS CLI: `rbac:sync:user-groups <tenant>` (`TENANT`: `SGP`, `HKG`, `AUS`, `GBR`) — not an end-user HTTP route |
| **Short Description** | Loads all non-default groups from the configured repository client (`SleekBackClient` when `repository_client` is `SLEEK_BACK`), then for each group gets or creates a matching JumpCloud user group (serialized name per env/tenant) and assigns that user group to the JumpCloud application. Does not sync individual user membership (see `rbac:sync:user-group-members`). |
| **Variants / Markets** | SG, HK, AU, UK (driven by `TENANT` enum passed to the command) |
| **Dependencies / Related Flows** | Sleek Back HTTP API (`SleekBackProxy.getGroups`); JumpCloud Directory API (`JumpCloudProxy`); companion CLI `rbac:sync:user-group-members` (`syncGroupMembers` — includes members); `RbacService.addUserToGroup` / `removeUserFromGroup` for ad hoc membership changes |
| **Service / Repository** | `sleek-auth` — `src/modules/rbac/rbac.service.ts` (`syncUserGroups`), `src/modules/rbac/rbac.command.ts`, `src/modules/rbac/repository-clients/sleek-back.client.ts` (`getGroups`); `src/modules/jumpcloud/jumpcloud.service.ts` (`getOrCreateUserGroupByName`, `assignUserGroupToApplication`) |
| **DB - Collections** | N/A (Sleek Back and JumpCloud HTTP APIs only; no MongoDB in this path) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `rbac.command.ts`

- Command `rbac:sync:user-groups` with positional `tenant`; calls `this.rbacService.syncUserGroups(tenant)`.

### `rbac.service.ts` — `syncUserGroups`

- `getRepositoryClient(tenant)` → `SleekBackClient` when `repository_client` config is `REPOSITORY_CLIENT.SLEEK_BACK`.
- `repository.getGroups()` then for each `group`: `jumpcloudService.getOrCreateUserGroupByName` with `group.name`, `group.group_slug`, `tenant`.
- `jumpcloudService.assignUserGroupToApplication(userGroup.id)` inside try/catch; errors logged via `loggerService.error`, not rethrown for individual groups.

### `rbac/.../sleek-back.client.ts` — `getGroups`

- Seeds pagination with `skip: 0`, `limit: 20`, `exclude_default_group: true`; `paginateGroups` walks `clientProxy.getGroups` until all pages are collected.

### `jumpcloud.service.ts`

- `serializeUserGroupName`: prefixes with `Admin Platform`, `NODE_ENV`, and tenant, then the group label.
- `getOrCreateUserGroupByName`: `getUserGroupByName` on serialized name; if missing, `createUserGroup` with static membership and `attributes.group` set to `{tenant}.{slug}`.
- `assignUserGroupToApplication`: `manageApplicationAssociation` ADD `USER_GROUP` to configured `jumpcloud.application_id`.
