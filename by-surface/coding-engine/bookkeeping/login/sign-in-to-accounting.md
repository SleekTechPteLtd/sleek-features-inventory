# Sign in to accounting

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sign in to accounting |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance user (accounting workspace) |
| **Business Outcome** | Users can access the Sleek CIT accounting workspace securely via Auth0 while returning to the page they intended or a sensible default. |
| **Entry Point / Surface** | Sleek CIT app root (`/`) when not authenticated; unauthenticated visits to protected routes redirect to `/` and preserve the intended URL for after login (`USER_ENTERED_URL`). |
| **Short Description** | Renders Auth0 Lock using platform config (client, domain, audience, connection, branding). On successful authentication, stores the access token in React context and `localStorage`, refreshes cached platform config, then redirects in order: saved `USER_ENTERED_URL`, `redirect` query parameter, or default landing (`/`). Invalid redirect targets are passed through `encodeURIComponent` when they fail a safe URL regex. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Auth0** (Auth0 Lock); **platform API** `GET /platform/config` (Auth0 and app settings via `getPlatformConfig`); **platform API** `GET /platform/user` (loads current user after token exists — `AuthProvider`); **ProtectedRoute** saves `window.location.href` to `USER_ENTERED_URL` when accessing protected routes while logged out. |
| **Service / Repository** | sleek-cit-ui |
| **DB - Collections** | None in this repo (session token and `platformConfig` in `localStorage`; user profile from `platform/user`). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether all regional deployments use the same Auth0 connection defaults (`defaultDatabaseConnection` fallback `sleek-client`); whether the `encodeURIComponent` branch for failed `REDIRECT_RULE_REGEX` matches product intent for edge-case redirects. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Login surface and routing (`src/Main.js`, `src/pages.js`)

- `/`: If `AUTH_TOKEN_KEY` is absent, renders `<Login />`; if present, `<Navigate>` to `HOMEPAGE` (`/dashboard` per `commons/constants/app-constants.js`).
- Dedicated `/login` route is commented out in `pages.js`; sign-in is anchored at `/`.

### Auth0 Lock and post-login redirect (`src/components/login/index.js`)

- Loads `getPlatformConfig()` then reads `auth0` (clientId, domain, audience, configurationBaseUrl, connection).
- Instantiates `Auth0Lock` with theme, `languageDictionary` title from platform name, `defaultDatabaseConnection` or `sleek-client`, sign-up and forgot-password disabled.
- `authenticated` handler: `onAuthSet(accessToken)`; `localStorage.setItem(AUTH_TOKEN_KEY, accessToken)`; `getPlatformConfig()`; `handleRedirect()`; `auth0.hide()`.
- `handleRedirect`: (1) `localStorage.getItem("USER_ENTERED_URL")` → navigate; (2) else `getRedirectUrlFriendly("redirect")` from query string; (3) else `DEFAULT_LANDING_PAGE` (`/`). Uses `REDIRECT_RULE_REGEX` from `utils/constants.js` — allowed chars pass through as `href`; otherwise `encodeURIComponent(redirect)`.

### Session and user context (`src/auth/authProvider.js`)

- `onAuthSet` / `handleAuthSetter`: updates React state and persists `AUTH_TOKEN_KEY`.
- On mount, `getToken()` reads token from `localStorage` and, when present, `GET platform/user` via `customAxiosInstance` to populate `currentLoggedInuser`.
- `onLogout` clears token and `CMS_CONFIG_KEY`.

### Query helper (`src/utils/auth-utils.js`)

- `getRedirectUrlFriendly(name)`: parses current `window.location.href` for named query parameter (used for `redirect`).

### Platform config (`src/utils/config-loader.js`)

- `getPlatformConfig`: returns cached JSON from `localStorage` key `platformConfig` or fetches `GET /platform/config` and caches it.

### Deep-link preservation (`src/auth/protectedRoute.js`)

- When `USER_ENTERED_URL` is not set, stores `window.location.href` before redirecting unauthenticated users to `/`, so login can return them to the intended protected URL.

### Constants (`src/utils/constants.js`)

- `AUTH_TOKEN_KEY` = `user_auth_token`; `REDIRECT_RULE_REGEX`; `DEFAULT_LANDING_PAGE` = `/`; `PLATFORM_NAME` = `Sleek CIT`.
