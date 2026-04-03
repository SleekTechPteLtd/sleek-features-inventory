# View signed-in user identity

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | View signed-in user identity |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User (authenticated SleekBooks API caller; typically the client app on behalf of the signed-in user) |
| **Business Outcome** | Callers resolve who is signed in for the current SleekBooks session so the app can personalize behaviour, enforce access, and stay aligned with the authoritative user record in Sleek Back. |
| **Entry Point / Surface** | SleekBooks service API: HTTP `GET /platform/user` under Swagger tag `platform`; requires a valid `Authorization` header. |
| **Short Description** | The platform controller returns the current user object attached to the request after `SleekBackAuthGuard` validates the caller’s bearer token by calling Sleek Back `GET /users/me` and attaching the JSON body to `request.user`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Sleek Back user API (`SLEEK_BACK_API_BASE_URL`); public platform bootstrap and Auth0 settings via [`configure-sign-in-and-platform-branding.md`](configure-sign-in-and-platform-branding.md) (`GET /platform/config`). |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | None |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Guard resolves with `resolve(request)` on success (truthy but non-boolean); confirm intended contract vs `resolve(true)`. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/platform/platform.controller.ts`

- `@Controller('platform')`; `@Get('/user')`; `@ApiOperation({ summary: 'Get User' })`; `@UseGuards(SleekBackAuthGuard)`.
- Handler returns `response.status(HttpStatus.OK).json(request.user)`.

### `src/common/guards/sleek-back.auth.guard.ts`

- `SleekBackAuthGuard`: requires `Authorization` header; otherwise `ForbiddenException('Access Forbidden')`.
- Forwards `authorization` and optional `app-origin` (default `admin`) on the HTTP client, then `GET` `${process.env.SLEEK_BACK_API_BASE_URL}/users/me`.
- On HTTP 200, assigns `request.user = data` from the response body; promise resolves so the route can run.
