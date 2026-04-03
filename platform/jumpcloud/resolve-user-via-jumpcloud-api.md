# Resolve user via JumpCloud API

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | Resolve user via JumpCloud API |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (JumpCloudService and internal callers) |
| **Business Outcome** | Resolves a JumpCloud directory user by email so downstream flows (HTTP lookup, user-group membership) can act on a stable `User` record. |
| **Entry Point / Surface** | Internal: `JumpCloudService.getUserByEmail`; indirectly `GET /jumpcloud/user-by-email` (see `resolve-user-identity-by-email-for-jumpcloud-integrations.md`) and group membership methods that call `getUserByEmail` first. |
| **Short Description** | The service asks `JumpCloudProxy.getUserDetails` for `GET /api/systemusers` with filter `email:eq:{email}` and uses the first result. If none, it throws `UserNotFoundError` (HTTP 404). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | JumpCloud Directory API (`console.jumpcloud.com` base URL from config); `BaseProxy` (Axios, `x-api-key`, correlation id). Downstream: `assignUserToUserGroupByEmail`, `removeUserFromUserGroupByEmail`; HTTP: `JumpCloudController.getUserByEmail`. Related doc: `resolve-user-identity-by-email-for-jumpcloud-integrations.md`. |
| **Service / Repository** | `sleek-auth` — `src/modules/jumpcloud/jumpcloud.service.ts`, `src/modules/jumpcloud/jumpcloud.proxy.ts`, `src/modules/jumpcloud/errors/user-not-found.error.ts` |
| **DB - Collections** | N/A (JumpCloud HTTP API only; no MongoDB on this path) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `jumpcloud.service.ts`

- `getUserByEmail(email)` calls `this.proxy.getUserDetails(\`email:eq:${email}\`)`.
- If falsy, throws `new UserNotFoundError(email)`; otherwise returns `User`.
- Used by `assignUserToUserGroupByEmail` and `removeUserFromUserGroupByEmail` after resolution.

### `jumpcloud.proxy.ts`

- `getUserDetails(filter)` — `GET /api/systemusers` with `params: { filter }`.
- Parses `GetUserResponse`: logs `totalCount`; returns `data.results[0]` when present, else `null`.
- HTTP errors go through `responseErrorInterceptor` → `JumpCloudApiError`.

### `errors/user-not-found.error.ts`

- `UserNotFoundError` extends `HttpException`: status `404`, message `User Not Found`, description includes email.

### Callers (context)

- `jumpcloud.controller.ts` — `getUserByEmail` → service, then `pick(user, ['_id', 'lastname', 'firstname', 'email'])` for the API response.
