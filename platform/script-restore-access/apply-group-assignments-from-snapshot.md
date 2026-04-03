# Apply group assignments from snapshot

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | Apply group assignments from snapshot |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (ops / engineer running CLI) |
| **Business Outcome** | Reconcile JumpCloud user–group membership from a checked-in JSON snapshot when access must be bulk-restored or aligned after an incident or data drift. |
| **Entry Point / Surface** | `sleek-auth` Nest CLI: `script:restore-access <tenant>` (nestjs-command); no end-user UI. |
| **Short Description** | Loads per-tenant user JSON from `src/scripts/data/{tenant}-users.json`, then for each user and each listed group calls `RbacService.addUserToGroup`, which ensures the JumpCloud user group exists and assigns the user by email. |
| **Variants / Markets** | SG, HK, UK, AU (tenant enum `SGP`, `HKG`, `GBR`, `AUS`) |
| **Dependencies / Related Flows** | JumpCloud (`JumpCloudService` via `RbacService`); related bulk sync paths `RbacService.syncUserGroups` / `syncGroupMembers` (repository + JC, not used by this script). |
| **Service / Repository** | `sleek-auth` |
| **DB - Collections** | None on this path (`addUserToGroup` uses JumpCloud APIs only). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether `AUS` / `GBR` snapshot JSON files are maintained off-repo; command description typo “Acccess” / “JC” scope. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/scripts/restore-access.script.ts`

- Command `script:restore-access` with positional `tenant` (`TENANT`).
- Reads `readFileSync(\`${__dirname}/data/${tenant}-users.json\`)`, parses JSON array of users with `email` and `groups` (`name`, `slug`).
- Per pair: `await this.rbacService.addUserToGroup({ email, group_name: group.name, group_slug: group.slug, country_code: tenant })`.
- Per-assignment errors are logged to `console.error` and skipped; fatal errors exit `1`.

### `src/modules/rbac/rbac.service.ts`

- `addUserToGroup(dto)`: `jumpcloudService.getOrCreateUserGroupByName` then `assignUserToUserGroupByEmail(dto.email, userGroup.id)`.

### Data layout

- Repo contains `src/scripts/data/SGP-users.json` and `HKG-users.json` (snapshots for those tenants).
