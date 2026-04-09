# Complete IRAS authorization

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Complete IRAS authorization |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Authenticated user (CIT app session; user completing IRAS OAuth redirect) |
| **Business Outcome** | After consenting at IRAS, the user returns to Sleek with an authorization code; the platform exchanges it for an access token so Corporate Income Tax flows can integrate with Singapore tax authority services. |
| **Entry Point / Surface** | Sleek CIT UI: OAuth callback route `/iras-auth` (query param `code` from IRAS redirect). Registered in `src/pages.js` with `requiresAuth: true`. |
| **Short Description** | On load, the page reads the OAuth `code` from the URL, calls the backend `POST /iras-auth` with `{ code }` using the authenticated axios client, and on success (response includes `data.token`) navigates the user to `/dashboard`. While waiting, it shows a minimal “Loading” state. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | Backend: `POST {baseURL}/iras-auth` (token exchange and persistence live server-side; `baseURL` from `getAPIBaseUrl()` in `axios-defaults.js` — e.g. `api-cit` hosts in non-local environments). Related CIT flows that surface IRAS consent or data (e.g. Form CS prefill/submission via `iras-utils.js`, computation steps linking to mytax.iras.gov.sg) assume a completed authorization path for API-backed IRAS integration. |
| **Service / Repository** | sleek-cit-ui (UI callback); backend API host as configured for CIT (`api-cit` / local) |
| **DB - Collections** | Unknown (no client-side persistence in these files; token handling is server-side) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether failed exchange or missing `code` should show an error UI (current code only `console.error`s on failure and still shows “Loading”). Whether `response.data.token` is persisted only on the server or also expected client-side (not stored in local state beyond a `console.log`). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Route registration

- `src/pages.js`: `IRASAuth` component, `url: "/iras-auth"`, `requiresAuth: true` (only authenticated users hit this callback).

### OAuth callback and token exchange

- `src/components/iras-auth/index.js`: `useSearchParams()` → `code` from `searchParams.get("code")`; `useEffect` calls `getIRASAuthToken()` when `code` is in the dependency array.
- `getIRASAuthToken`: `customAxiosInstance.post(\`/iras-auth\`, { code })` — sends Bearer token from `localStorage` per `src/utils/axios-defaults.js`.
- Success path: if `response.data.token` is truthy, `navigate(\`/dashboard\`)`.
- UI: `Box` with text “Loading” during the operation.

### HTTP client

- `src/utils/axios-defaults.js`: `getAPIBaseUrl()` selects CIT API base (`api-cit-sit`, `api-cit-staging`, `api-cit`, or localhost); requests include `Authorization: Bearer ${localStorage.getItem(AUTH_TOKEN_KEY)}`.

### Related (not this feature’s core)

- `src/utils/iras-utils.js`: Form CS prefill/submission helpers to other API paths (`/form-cs/...`), separate from the `/iras-auth` callback.
