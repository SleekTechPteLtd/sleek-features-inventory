# Tenant RBAC user groups sync CLI

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | Tenant RBAC user groups sync CLI |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operator (platform / internal) |
| **Business Outcome** | Ensures JumpCloud user groups exist and are associated with the configured JumpCloud application for each RBAC group returned by Sleek Back for a tenant, so directory-backed SSO access can use those groups before or without running member sync. |
| **Entry Point / Surface** | `sleek-auth` NestJS CLI: `nestjs-command` entry (`src/cli.ts`) — command `rbac:sync:user-groups` with tenant positional; README documents `npx nestjs-command rbac:sync:user-groups --tenant=<TENANT>` with `secrets-init` in front when needed. |
| **Short Description** | Operator runs a one-shot sync for a given tenant: loads groups from the configured repository client (Sleek Back via `SleekBackClient`), ensures each group exists in JumpCloud (`getOrCreateUserGroupByName`), and associates it with the JumpCloud SSO application (`assignUserGroupToApplication`). Does not add or remove users in groups. Exits 0 on completion of the loop or 1 if `syncUserGroups` throws. |
| **Variants / Markets** | SG, HK, AU, UK (tenant enum `TENANT`: SGP, HKG, AUS, GBR) |
| **Dependencies / Related Flows** | Sleek Back HTTP API (groups via `SleekBackClient.getGroups` / `SleekBackProxy.getGroups`); JumpCloud Directory API via `JumpCloudService` (`getOrCreateUserGroupByName`, `assignUserGroupToApplication`); sibling CLI `rbac:sync:user-group-members` (adds members per group); optional relationship to HTTP RBAC endpoints (`RbacController` add/remove user from group). |
| **Service / Repository** | `sleek-auth` — `src/modules/rbac/rbac.command.ts`, `rbac.service.ts`, `rbac.module.ts`; `src/modules/rbac/repository-clients/sleek-back.client.ts`; `src/modules/shared/proxies/sleek-back/sleek-back.proxy.ts`; `src/modules/jumpcloud/jumpcloud.service.ts`, `jumpcloud.proxy.ts`; `src/cli.ts`; `README.md` (example invocation) |
| **DB - Collections** | N/A in this path (`sleek-auth` uses Sleek Back and JumpCloud HTTP APIs; no MongoDB access in this RBAC sync flow). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | README uses `--tenant=<TENANT>` while `rbac.command.ts` declares a positional `tenant`; confirm the exact CLI argv shape for the deployed `nestjs-command` version if operators see parse errors. Per-group `assignUserGroupToApplication` failures are logged but not rethrown—document whether partial success is acceptable for operators. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `rbac.command.ts`

- `@Command({ command: 'rbac:sync:user-groups', describe: 'Sync user groups to JC' })` on `syncUserGroups`.
- Positional `tenant` typed as `TENANT`; calls `this.rbacService.syncUserGroups(tenant)`.
- `try` / `catch`: success logs `Synced` and `process.exit(0)`; failure logs error and `process.exit(1)`.

### `rbac.service.ts` — `syncUserGroups`

- `getRepositoryClient(tenant)` → `SleekBackClient` when `repository_client` config is `REPOSITORY_CLIENT.SLEEK_BACK`.
- `repository.getGroups()`: paginates with `exclude_default_group: true`, `limit` 20.
- For each group: `jumpcloudService.getOrCreateUserGroupByName` with `name`, `slug: group.group_slug`, `tenant`; then `assignUserGroupToApplication(userGroup.id)` inside `try` / `catch` that logs errors from JumpCloud but does not rethrow.

### `sleek-back.client.ts`

- `getGroups` delegates to `SleekBackProxy.getGroups` with tenant-scoped config (`sleek_back` per-tenant `base_url`, client credentials).

### CLI bootstrap

- `src/cli.ts`: `NestFactory.createApplicationContext(AppModule)`, `CommandModule` + `CommandService.exec()`.

### `README.md`

- Documents: `/secrets-init/bin/secrets-init npx nestjs-command rbac:sync:user-groups --tenant=SGP`.

### Tests

- `src/modules/rbac/specs/rbac.command.spec.ts` — `syncUserGroups` invokes `RbacService.syncUserGroups` and exit codes on failure.
