# Resolve user identity by email for JumpCloud integrations

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Platform |
| **Feature Name** | Resolve user identity by email for JumpCloud integrations |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Machine-authenticated callers can map an email to a Sleek user id and minimal profile fields so JumpCloud-related integrations resolve identity without receiving full JumpCloud user records. |
| **Entry Point / Surface** | `sleek-auth` HTTP API: `GET /jumpcloud/user-by-email?email=` (M2M / Basic-secured; not an end-user app screen) |
| **Short Description** | Trusted services pass a required `email` query parameter. The service looks up the user in JumpCloud via the Directory API and returns only `_id`, `firstname`, `lastname`, and `email`. Responds with 404 when no user matches. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | JumpCloud Directory API (`GET /api/systemusers` with `email:eq:` filter via `JumpCloudProxy.getUserDetails`); `M2MAuthGuard` and `@ApiSecurity('basic')` from `@sleek-sdk/common`; same module reuses `JumpCloudService.getUserByEmail` for group membership by email (`assignUserToUserGroupByEmail`, `removeUserFromUserGroupByEmail`). |
| **Service / Repository** | `sleek-auth` — `src/modules/jumpcloud/jumpcloud.controller.ts`, `jumpcloud.service.ts`, `jumpcloud.proxy.ts`, `dto/get-user-by-email.dto.ts`, `docs/user-info-response.doc.ts`, `errors/user-not-found.error.ts` |
| **DB - Collections** | N/A (JumpCloud HTTP API only; no MongoDB on this path) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `jumpcloud.controller.ts`

- `GET /jumpcloud/user-by-email` with `@Query() GetUserByEmailDto` (`email` required).
- `@UseGuards(new M2MAuthGuard())`, `@ApiSecurity('basic')`.
- `@ApiOkResponse` type `UserInfoResponseDoc`; `@ApiNotFoundResponse` for missing user.
- Response: `pick(user, ['_id', 'lastname', 'firstname', 'email'])` — limits fields exposed to API callers.

### `get-user-by-email.dto.ts`

- `class-validator` `@IsNotEmpty()` on `email`; Swagger `ApiProperty` example `john.doe@sleek.com`.

### `user-info-response.doc.ts`

- Documents `_id`, `firstname`, `lastname`, `email` for OpenAPI.

### `jumpcloud.service.ts`

- `getUserByEmail(email)` → `this.proxy.getUserDetails(\`email:eq:${email}\`)`; throws `UserNotFoundError` when absent.
- Also used internally by `assignUserToUserGroupByEmail` and `removeUserFromUserGroupByEmail`.

### `jumpcloud.proxy.ts`

- `getUserDetails(filter)` — `GET /api/systemusers` with `filter` query param; returns first `results[0]` or `null`.

### Errors

- `UserNotFoundError` — HTTP 404, message `User Not Found`.
