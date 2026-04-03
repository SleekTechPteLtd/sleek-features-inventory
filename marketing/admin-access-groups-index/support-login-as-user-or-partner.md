# Support login as user or partner

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Support login as user or partner |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (full access to access management; partner flow additionally requires full partner access management when the feature is enabled) |
| **Business Outcome** | Staff can reproduce or assist with customer or partner sessions without sharing long-lived credentials, using a short-lived token handoff for troubleshooting and support. |
| **Entry Point / Surface** | Sleek Admin — Access Management — Groups (`pages/admin/access/groups/index.html.marko` → `src/views/admin/access/groups/index.js`); primary toolbar actions **Login As...** and **Login As Partner** (when `partner_access_management` CMS feature is enabled). |
| **Short Description** | From the groups view, admins request a single-use token for a target user email (and for partners, a domain). The browser redirects to the customer site or a partner URL with `sut=` (or legacy auth token flow when no customer website URL is configured). **Login As...** requires `access_management` permission `full`. **Login As Partner** requires `partner_access_management` permission `full`. |
| **Variants / Markets** | Unknown (redirect base URL comes from platform config / `getCustomerWebsiteUrl()`; partner domain is entered manually) |
| **Dependencies / Related Flows** | Upstream: SSO/group management flags (`sso.allow_group_management`), CMS `partner_access_management` feature, `getUser()` for permissions. Downstream: `POST` Sleek API `admin/users/get-single-use-authentication-token-impersonation` or `admin/users/get-authtoken` (when customer website URL empty), and `POST` `admin/users/partner-get-sut` for partners; customer/partner apps consume `sut` on landing. Related: broader Access Management groups (add/remove users) on the same page. |
| **Service / Repository** | `sleek-website` — `src/views/admin/access/groups/index.js`, `access-login-as-form.js`, `access-login-as-partner-form.js`, `src/utils/api.js` (`loginAsOtherUser`, `getLoginTokenForPartner`, `getAuthenticationToken`, `getPartnerSUTDetails`); backend: Sleek API admin user endpoints above |
| **DB - Collections** | None in this repo (tokens and user resolution live in API/backend) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `get-authtoken` vs impersonation endpoint differences are documented in API; validation rules for partner `domain` and `on_load_page` (returned by API) are not visible in this repo. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/access/groups/index.js`

- **`componentDidMount`:** Loads platform config and user; derives `disableUserManagement` from SSO `allow_group_management` and `user.permissions.access_management === "full"` (for group membership UI, not for login-as buttons).
- **`handleLoginAsClick` / `handleLoginAsPartner`:** Opens dialogs with `AccessLoginAsForm` or `AccessLoginAsPartnerForm`; `dialogDisableActions: true` (form-driven actions only).
- **`handleLoginAsSuccess(singleUseToken, domain="", onLoadPage="")`:** Builds redirect URL. If `domain` empty (user flow): navigates to `getCustomerWebsiteUrl()/profile/` with `?sut=${singleUseToken}` when customer URL is set; otherwise profile without query. If `domain` set (partner flow): `${domain}/${onLoadPage}/?sut=${singleUseToken}`.
- **`renderPrimaryToolbarContent`:** **Login As...** disabled unless `user.permissions.access_management === "full"`. **Login As Partner** shown only when `partner_access_management` app feature is enabled; disabled unless `user.permissions.partner_access_management === "full"`.

### `src/views/admin/access/groups/access-login-as-form.js`

- **Submit:** `api.loginAsOtherUser` with JSON body `{ email }`; `onSuccess` receives token string from API wrapper.

### `src/views/admin/access/groups/access-login-as-partner-form.js`

- **Submit:** `api.getLoginTokenForPartner` with `{ email, domain }`; success passes `singleUseToken`, `domain`, and `onLoadPage` from API response into parent `onSuccess`.

### `src/utils/api.js`

- **`loginAsOtherUser`:** If `getCustomerWebsiteUrl() === ""`, `POST` `${getBaseUrl()}/admin/users/get-authtoken`; else `POST` `${getBaseUrl()}/admin/users/get-single-use-authentication-token-impersonation`. Uses `getAuthenticationToken`, which returns `data.single_use_token` when present.
- **`getLoginTokenForPartner`:** `POST` `${getBaseUrl()}/admin/users/partner-get-sut`; `getPartnerSUTDetails` maps `data.single_use_token` and `data.on_load_page`.
