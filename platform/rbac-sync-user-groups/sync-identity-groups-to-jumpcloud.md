# Sync identity groups to JumpCloud

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | Sync identity groups to JumpCloud |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Keeps JumpCloud directory-backed groups and SSO application bindings aligned with Sleek Back product group definitions per tenant, so access policies that depend on JumpCloud user groups stay consistent with the source of truth. |
| **Entry Point / Surface** | CLI: `rbac:sync:user-groups <tenant>` (NestJS `nestjs-command`), run against a configured `sleek-auth` deployment with tenant-specific Sleek Back and JumpCloud settings. |
| **Short Description** | For a given tenant, the command loads RBAC groups from Sleek Back (paginated, excluding the default group), ensures each maps to a JumpCloud user group (create if missing with a serialized name and slug attributes), then associates each group with the configured JumpCloud SSO application. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** Sleek Back HTTP API via `SleekBackProxy.getGroups` (client credentials per tenant in `sleek_back` config). **Downstream:** JumpCloud Directory API via `JumpCloudProxy` — user group lookup/create, `manageApplicationAssociation` to bind groups to `jumpcloud.application_id`. **Related:** `rbac:sync:user-group-members` syncs membership after groups exist; `addUserToGroup` / `removeUserFromGroup` for ad-hoc membership changes. |
| **Service / Repository** | `sleek-auth` — `src/modules/rbac/rbac.command.ts`, `src/modules/rbac/rbac.service.ts`, `src/modules/rbac/repository-clients/sleek-back.client.ts`, `src/modules/jumpcloud/jumpcloud.service.ts` (and `jumpcloud.proxy.ts` transitively) |
| **DB - Collections** | N/A (Sleek Back and JumpCloud HTTP APIs only on this sync path; no direct MongoDB access in `syncUserGroups`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `rbac.command.ts`

- `@Command({ command: 'rbac:sync:user-groups', describe: 'Sync user groups to JC' })` — entry CLI.
- `syncUserGroups(tenant: TENANT)` calls `this.rbacService.syncUserGroups(tenant)`; exits `0`/`1`.

### `rbac.service.ts`

- `getRepositoryClient(tenant)` returns `SleekBackClient` when `repository_client` config is `SLEEK_BACK` (default from config).
- `syncUserGroups(tenant)`: `repository.getGroups()` then for each group `jumpcloudService.getOrCreateUserGroupByName({ name: group.name, slug: group.group_slug, tenant })`, then `assignUserGroupToApplication(userGroup.id)`; errors on application assignment are logged, not rethrown per group.

### `sleek-back.client.ts`

- `getGroups()`: paginates with `skip`/`limit` 20, `exclude_default_group: true`, aggregates via `paginateGroups` calling `clientProxy.getGroups`.

### `jumpcloud.service.ts`

- `serializeUserGroupName(name, tenant)` — builds display name: `Admin Platform [ENV] [TENANT] [name]`.
- `getOrCreateUserGroupByName`: resolves by serialized name via `getUserGroupByName`; else `createUserGroup` with `attributes.group` set to `{tenant}.{slug}`, `membershipMethod` static.
- `assignUserGroupToApplication(groupId)`: `manageApplicationAssociation` with `applicationId` from config, type `USER_GROUP`, operation `ADD`.
