# sleek-website — scan notes

Staff **admin** web app (Marko + React): `pages/admin/` routes, `src/views/admin/`, `src/utils/api.js` (multi-service bases).

## Authentication

Legacy **sleek-back** `/users/login`, `/users/logout`, forgot/reset password, plus **Auth0** / **SSO** when enabled via CMS features (`api-utils.js`, `getAuthClient`, Auth0 Lock in side menu). **Do not** duplicate **Sleek Auth** authentication rows for these; treat as legacy/migration context ([../../authentication/README.md](../../authentication/README.md#scope-no-duplicate-auth-rows)).

**Admin “login as”** (single-use token to open customer portal): documented as a **Platform** auth capability with legacy evidence and **Sleek Auth gap** in [../../authentication/admin-login-as-customer-single-use-token.md](../../authentication/admin-login-as-customer-single-use-token.md).

## Cross-repo map

Use [../../cross-repo-sleek-surfaces-map.md](../../cross-repo-sleek-surfaces-map.md) for admin IA ↔ **sleek-back** / other services ↔ **audit Domain** hints.

## Evidence hotspots

- `pages/admin/**/*.html.marko` — routable admin pages (run `node scripts/pages.js --list` in repo for full list)
- `src/components/new-admin-side-menu.js` — primary nav links
- `src/utils/api.js` — `API_BASE_URL`, `/admin` path rewriting, subscription/payment/file/deadline/company-roles URLs
- `src/utils/api-utils.js` — request headers for admin Auth0 / SSO

## Customer app from admin

`new-admin-side-menu.js` opens **customer-mfe** sleek-sign via `getCustomerWebsiteUrl() + /sleek-sign/...?origin=admin` (see cross-repo map).

## Related

- [sleek-back README](../sleek-back/README.md)
- [customer-mfe README](../customer-mfe/README.md)
- [Platform root README](../../README.md)
