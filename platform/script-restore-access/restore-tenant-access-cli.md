# Restore tenant access (CLI)

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Restore tenant access from CLI |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operator (internal) |
| **Business Outcome** | Replay JumpCloud group memberships for users when restoring from a captured JSON snapshot (e.g. after incident or environment repair). |
| **Entry Point / Surface** | **sleek-auth** CLI: `script:restore-access <tenant>` (nestjs-command); JSON input at `src/scripts/data/{tenant}-users.json` relative to compiled script `__dirname`. |
| **Short Description** | Reads a per-tenant user snapshot file, iterates each user’s `groups`, and calls `RbacService.addUserToGroup` for every pair so JumpCloud user groups are ensured and users are assigned by email. Per-assignment errors are logged to stderr; script exits 0 on completion of the loop or 1 on file/parse failure. |
| **Variants / Markets** | SGP, HKG, AUS, GBR (matches `TENANT` enum and sample `*-users.json` files) |
| **Dependencies / Related Flows** | `RbacService.addUserToGroup` (same behavior as HTTP `POST` RBAC assign path); JumpCloud user groups and user–group membership; optional relation to broader RBAC / `script:sync-*` flows |
| **Service / Repository** | `sleek-auth` |
| **DB - Collections** | None on this path — `addUserToGroup` uses JumpCloud APIs only (no MongoDB read/write in `rbac.service.ts` for this method). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Who produces and checks in `data/{tenant}-users.json`; whether this remains the preferred DR path vs `syncGroupMembers`; typo in logger name `restore-acces` — intentional or fix? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/scripts/restore-access.script.ts` — `@Command` `script:restore-access`, positional `tenant` typed as `TENANT`, reads `readFileSync(\`${__dirname}/data/${tenant}-users.json\`)`, loops `user.groups`, calls `this.rbacService.addUserToGroup({ email, group_name, group_slug, country_code: tenant })`.
- `src/modules/rbac/rbac.service.ts` — `addUserToGroup`: `jumpcloudService.getOrCreateUserGroupByName` then `assignUserToUserGroupByEmail`.
- `src/modules/jumpcloud/jumpcloud.service.ts` — `getOrCreateUserGroupByName`, `assignUserToUserGroupByEmail`.
- `src/modules/shared/shared.enum.ts` — `TENANT` values `SGP`, `HKG`, `AUS`, `GBR`.
- Example snapshot files: `src/scripts/data/SGP-users.json`, `src/scripts/data/HKG-users.json`.
