# Tenant RBAC group member sync CLI

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | Tenant RBAC group member sync CLI |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operator (platform / internal) |
| **Business Outcome** | Keeps JumpCloud user-group membership aligned with Sleek Back group membership per tenant so SSO and directory-backed access stay correct after changes in the source system. |
| **Entry Point / Surface** | `sleek-auth` NestJS CLI: `nestjs-command` entry (`src/cli.ts`) — command `rbac:sync:user-group-members` with tenant positional; README documents `npx nestjs-command rbac:sync:user-group-members --tenant=<TENANT>` with secrets-init in front when needed. |
| **Short Description** | Operator runs a one-shot sync for a given tenant: loads groups from the configured repository client (Sleek Back), resolves members per group, ensures the corresponding JumpCloud user group exists, associates the group with the JumpCloud application, and adds each member user to that group by email. Exits 0 on success and 1 on failure. |
| **Variants / Markets** | SG, HK, AU, UK (tenant enum `TENANT`: SGP, HKG, AUS, GBR) |
| **Dependencies / Related Flows** | Sleek Back HTTP API (groups via `SleekBackClient.getGroups`, members via `SleekBackClient.getUsersByGroupId` / `getGroupMembers`); JumpCloud Directory API via `JumpCloudService` (`getOrCreateUserGroupByName`, `assignUserGroupToApplication`, `assignUserToUserGroupByEmail`); sibling CLI `rbac:sync:user-groups` (syncs group definitions and app association without member iteration); optional relationship to HTTP RBAC endpoints (`RbacController` add/remove user from group). |
| **Service / Repository** | `sleek-auth` — `src/modules/rbac/rbac.command.ts`, `rbac.service.ts`, `rbac.module.ts`; `src/modules/user/user.service.ts`, `src/modules/user/repository-clients/sleek-back.client.ts`; `src/modules/rbac/repository-clients/sleek-back.client.ts`; `src/modules/jumpcloud/jumpcloud.service.ts`, `jumpcloud.proxy.ts`; `src/cli.ts`; `README.md` (example invocation) |
| **DB - Collections** | N/A in this path (`sleek-auth` uses Sleek Back and JumpCloud HTTP APIs; no MongoDB access in the RBAC sync flow). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | README uses `--tenant=<TENANT>` while `rbac.command.ts` declares a positional `tenant`; confirm the exact CLI argv shape for the deployed `nestjs-command` version if operators see parse errors. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `rbac.command.ts`

- `@Command({ command: 'rbac:sync:user-group-members', describe: 'Sync user group members to JC' })` on `syncUserGroupMembers`.
- Positional `tenant` typed as `TENANT`; calls `this.rbacService.syncGroupMembers(tenant)`.
- `try` / `catch`: success logs `Synced` and `process.exit(0)`; failure logs error and `process.exit(1)`.

### `rbac.service.ts` — `syncGroupMembers`

- `getRepositoryClient(tenant)` → `SleekBackClient` when `repository_client` is `SLEEK_BACK`.
- `repository.getGroups()` then for each group: `userService.getUsersByGroupId` with `group_id`, `tenant`, `exclude_non_sleek_user: true`; skips groups with no members.
- For each group with members: `jumpcloudService.getOrCreateUserGroupByName`, `assignUserGroupToApplication` (errors logged, rethrown from JC path), then per member `assignUserToUserGroupByEmail`.

### CLI bootstrap

- `src/cli.ts`: `NestFactory.createApplicationContext(AppModule)`, `CommandModule` + `CommandService.exec()`.

### `README.md`

- Documents: `/secrets-init/bin/secrets-init npx nestjs-command rbac:sync:user-group-members --tenant=SGP`.

### Tests

- `src/modules/rbac/specs/rbac.command.spec.ts` — `syncUserGroupMembers` invokes `RbacService.syncGroupMembers` and exit codes on failure.
