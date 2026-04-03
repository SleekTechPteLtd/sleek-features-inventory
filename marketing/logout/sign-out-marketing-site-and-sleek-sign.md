# Sign out from marketing site and Sleek Sign

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Sign out from marketing site and Sleek Sign |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Visitor |
| **Business Outcome** | Visitors can end their session on the marketing site and signal the embedded Sleek Sign app to log out, then land back on the public marketing home without stale client-side session data. |
| **Entry Point / Surface** | Sleek marketing site — `/logout/` webpack entry `logout` → `LogoutView` (`src/views/logout.js`). The same `logoutToSleekSignPlatform` + `SLEEK_SIGN_URL` pattern is reused from menus and other views (e.g. `user-menu.js`, `side-menu.js`, `verify.js`). |
| **Short Description** | On the dedicated logout page, the app reloads the hidden Sleek Sign iframe (`app_iframe`) to the environment’s `security.html` URL. When the iframe loads, it posts a cross-origin `postMessage` that instructs the embedded app to apply a logout payload in storage, then runs a callback that clears all keys in the `store` wrapper and sets `window.location` to `/` (marketing home). |
| **Variants / Markets** | SG, HK (and other hosts mapped in `SLEEK_SIGN_URL` / `SLEEK_SIGN_URL_DOMAIN` for sit, staging, production, and blue variants) |
| **Dependencies / Related Flows** | **Downstream / integration:** Sleek Sign web app (`…/security.html`) must accept the `postMessage` storage protocol. **Same-repo:** `store` for persisted client session; menu-driven logout flows that call `logoutToSleekSignPlatform` before API `users/logout` or Auth0 / `AuthClient` logout in admin paths. **`logout-listener.js`** is stubbed (no cross-tab storage listener). |
| **Service / Repository** | `sleek-website` — `src/views/logout.js`, `src/utils/logout-to-sleeksign.js`, `src/utils/constants.js` (`SLEEK_SIGN_URL`, related sign host maps) |
| **DB - Collections** | None in this repo (client session via `store` / underlying storage; no MongoDB) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `postMessage(..., "*")` uses a wildcard target origin — confirm security review aligns with Sleek Sign’s listener. If `window.location.host` is absent from `SLEEK_SIGN_URL`, `iframe.src` may be invalid; confirm all production marketing hosts are covered. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/logout.js`

- **Entry:** `domready` mounts `LogoutView` on `#root`.
- **`LogoutView` constructor:** Calls `logoutToSleekSignPlatform(SLEEK_SIGN_URL[window.location.host], 'app_iframe', callback)`.
- **Callback:** `store.clearAll()` then `window.location = "/"` (return to marketing home).
- **UI:** `render()` returns `null` — no visible chrome; behavior is entirely side effects.

### `src/utils/logout-to-sleeksign.js`

- **`logoutToSleekSignPlatform(domain, htmlId, callback)`:** Resolves `document.getElementById(htmlId)`, sets `iframe.onload` to:
  - Read `iframe.contentWindow` (try/catch for cross-origin edge cases).
  - Build payload `{ action: "Logout", isSleekPayload: true }`.
  - `postMessage(JSON.stringify({ key: 'storage', method: "set", data: payload }), "*")` into the iframe window so Sleek Sign can clear or replace session state in its storage bridge.
  - Invoke `callback()` (marketing site then clears `store` and redirects in `logout.js`).
- **Reload:** Sets `iframe.src = domain` so the iframe loads the Sleek Sign `security.html` page before `onload` fires.

### `src/utils/constants.js`

- **`SLEEK_SIGN_URL`:** Maps `window.location.host` (e.g. `app.sleek.sg`, `app.sleek.hk`, localhost, sit/staging/blue variants) to the corresponding Sleek Sign `security.html` URL used as the iframe `domain` argument.
- **Related exports (context for Sleek Sign embedding elsewhere):** `SLEEK_SIGN_URL_DOMAIN`, `SLEEK_SIGN_HOST_NAME_DOMAIN` — base sign app origins by host.

### Build wiring (supporting)

- **`webpack/paths.js`:** `"logout": "./src/views/logout.js"`.
- **`webpack/webpack.common.js`:** HTML output `logout/index.html`, chunk `logout`.
