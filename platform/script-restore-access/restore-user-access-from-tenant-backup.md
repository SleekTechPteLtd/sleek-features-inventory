# Restore user access from tenant backup

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | Restore user access from tenant backup |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | After an incident or environment repair, JumpCloud RBAC matches a known per-tenant snapshot so users regain the correct group memberships. |
| **Entry Point / Surface** | **sleek-auth** CLI: `script:restore-access <tenant>` (nestjs-command); JSON at `src/scripts/data/{tenant}-users.json` (resolved from compiled script `__dirname`). |
| **Short Description** | Operators run the command with a tenant key; the script loads a JSON export of users and their groups, then bulk-assigns each user to each listed group via `RbacService.addUserToGroup`, which ensures JumpCloud user groups exist and binds users by email. |
| **Variants / Markets** | SGP, HKG, AUS, GBR (via `TENANT`; aligns with sample `*-users.json` in repo) |
| **Dependencies / Related Flows** | JumpCloud user groups and membership (`JumpCloudService`); same `addUserToGroup` behavior as HTTP RBAC assign; related sync CLIs `RbacService.syncUserGroups` / `syncGroupMembers` (repository-driven, not used by this script). |
| **Service / Repository** | `sleek-auth` |
| **DB - Collections** | None on this path — `addUserToGroup` calls JumpCloud APIs only (no MongoDB in this method). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Who authors and validates `data/{tenant}-users.json` for each restore; whether DR preference is this snapshot replay vs `syncGroupMembers`; logger name typo `restore-acces` and command description typo “Acccess” — fix or leave? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `sleek-auth/src/scripts/restore-access.script.ts`

- `@Command({ command: 'script:restore-access', describe: 'Restore Acccess to JC' })`, positional `tenant: TENANT`.
- `readFileSync(\`${__dirname}/data/${tenant}-users.json\`)`, JSON array parsed to `users`.
- For each `user`, for each `user.groups`: `await this.rbacService.addUserToGroup({ email: user.email, group_name: group.name, group_slug: group.slug, country_code: tenant })`.
- Per-assignment failures: `console.error(error)`; loop continues. Fatal read/parse: `process.exit(1)`; success: `process.exit(0)`.

### `sleek-auth/src/modules/rbac/rbac.service.ts`

- `addUserToGroup(dto: AddUserToGroupDto)`: `jumpcloudService.getOrCreateUserGroupByName({ name, slug, tenant: country_code })` then `jumpcloudService.assignUserToUserGroupByEmail(dto.email, userGroup.id)`.

### Snapshot data

- Examples in repo: `src/scripts/data/SGP-users.json`, `src/scripts/data/HKG-users.json`.
