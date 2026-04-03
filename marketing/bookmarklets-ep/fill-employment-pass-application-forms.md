# Fill Employment Pass application forms from Sleek records

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Fill Employment Pass application forms from Sleek records |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (authenticated staff; `user.profile === "admin"`) |
| **Business Outcome** | Staff can copy Sleek-held Employment Pass applicant data into the official online application form so submission requires less retyping and fewer copy-paste errors. |
| **Entry Point / Surface** | **Bookmarklet / injected script** on the **official Singapore EP application site** (target page exposes the `form` fields the overlay writes to). The built bundle is **`src/bookmarklets/ep.js`** (served for bookmarklet use; local dev snippet in file comments loads e.g. `http://localhost:5000/bookmarklets/ep.js`). On load, **`EPPluginOverlay`** mounts in a full-page `div.react-root` and shows **“Sleek FormFill”**. |
| **Short Description** | Admins sign in with email/password (or reuse session). The overlay lists **non-draft** EP applicants (`status !== "draft"`), loads full **`/eps/:id`** payload, shows **education**, **memberships**, and **file** sections for review, then **Fill Form** maps `selectedEp.data` onto named inputs/selects/radios on the host page (`applnView.*`, `applnJobView[*]`, etc.). File names link via **`getFileBaseUrl()/files/:id`** for download. |
| **Variants / Markets** | **SG** (Employment Pass / MOM-style application form field names in code). |
| **Dependencies / Related Flows** | **API** (`src/utils/api.js`): `logIn` → `POST /users/login`; `getUser` → `GET /admin/users/me`; `getEps` → `GET /eps`; `getEp` → `GET /eps/:epId`. **Auth**: `user_auth_token` in `store` from login. **Files**: `getFileBaseUrl()` (files microservice or API fallback). **Helpers**: `src/utils/date`, `src/utils/countries`, `src/utils/view` (`downloadFile`). **Logout**: `logoutToSleekSignPlatform` + `SLEEK_SIGN_URL` for iframe/sign platform. **Upstream**: EP records and attachments maintained in **sleek-back** (not read in this pass). **External**: Official EP site DOM must match selectors. |
| **Service / Repository** | **sleek-website**: `src/bookmarklets/ep.js`, `src/bookmarklets/ep.css`, `src/utils/api.js` (plus imported utils). **sleek-back**: implements `/eps`, `/users/login`, `/admin/users/me` — **not read in this pass**. |
| **DB - Collections** | **Unknown** from these files (all data via REST). EP persistence is server-side. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether `GET /eps` is scoped to the admin’s tenant or company on the server; whether excluding drafts in the UI only is sufficient for compliance; how often the government site’s form field `name`s change (bookmarklet would break). Whether education blocks beyond review are injected (only first two memberships / jobs mapped in `fillForm`). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-website — `src/bookmarklets/ep.js`

- **Mount**: Creates `body > .react-root`, renders `EPPluginOverlay`.
- **Admin gate**: Renders login form unless `get(this.state, "user.profile") === "admin"`; after login, `fetchUser` + `fetchEps`.
- **Data load**: `api.getUser()`; `api.getEps()` → list; `api.getEp(selectedEpId)` on applicant change.
- **Draft filter**: `eps.filter(ep => ep.status !== "draft")` for dropdown.
- **Applicant picker**: `<select name="selected_ep_id">`; labels from `employee_*` name fields or `user.email`.
- **Review UI**: `renderEducations` (employee + spouse), `renderMemberships`, `renderEpFiles` (top-level `*_files` keys and nested education files); certificate links use `api.getFileBaseUrl()`.
- **Fill**: `fillForm()` builds `fieldsData` with `fieldName` / `fieldType` / `value` from `selectedEp.data`, then `document.querySelector` for `input`, `radio`, `select` under `form` — maps personal info, travel document, address, memberships `[0]`/`[1]`, employment `[0]`/`[1]`, salary, declarations `antQ01`–`antQ06`, work visa declaration, etc. Country/demonyms via `getCountryData` / `getAlpha2CodeFromDemonym`. Dev-only `console.log` when `api.getBaseUrl() !== "https://api.sleek.sg"`.
- **Logout**: `store.clearAll()`, `logoutToSleekSignPlatform`, `window.location = "/"`.

### sleek-website — `src/bookmarklets/ep.css`

- **Layout**: Fixed overlay `.ep-plugin-overlay` (top-right, z-index 999, max-height 600px, Blueprint-style border). Typography and `details`/`summary` for collapsible sections; `.close` button positioned top-right.

### sleek-website — `src/utils/api.js`

- **`logIn`**: `POST ${getBaseUrl()}/users/login`, sets `store` `user_auth_token` from `data.auth_token`.
- **`getUser`**: `GET ${getBaseUrl()}/admin/users/me`.
- **`getEps`**: `GET ${getBaseUrl()}/eps`.
- **`getEp`**: `GET ${getBaseUrl()}/eps/${epId}`.
- **`getBaseUrl`**: production `https://api.sleek.sg`, else `http://localhost:3000` unless `API_BASE_URL` set.
- **`getFileBaseUrl`**: files microservice from platform config / env, else `getBaseUrl()` (used by overlay links, not only EP).
