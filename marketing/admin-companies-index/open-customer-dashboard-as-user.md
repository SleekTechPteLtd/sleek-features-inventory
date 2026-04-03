# Open customer dashboard as user

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Open customer dashboard as user |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Lets staff open the customer-facing dashboard in context of a chosen company to support users and verify what they see without sharing long-lived credentials. |
| **Entry Point / Surface** | Sleek CMS Admin **Companies** list (`/admin/companies/`) — per-company row action **View Dashboard** (share icon, title "View Dashboard") |
| **Short Description** | Requests a single-use dashboard token for the company, then opens a new browser tab to the customer site dashboard URL with `cid` and `sut` query parameters. Requires `CUSTOMER_WEBSITE_URL` to be set; otherwise the click does nothing after `preventDefault`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **API:** `POST {API_BASE_URL}/admin/users/get-single-use-authentication-token-dashboard` with JSON body `{ cid }` (company id). Response may return `data.single_use_token` (used for the URL) or `data.auth_token` (stored in local storage via `store.set` — same helper as other auth flows). **URL:** `{CUSTOMER_WEBSITE_URL}/dashboard/?cid={companyId}&sut={token}`. Same dashboard-open pattern exists on **Company overview** (`src/views/admin/company-overview/index.js`). Customer app must consume `sut` to establish session. |
| **Service / Repository** | `sleek-website` (admin UI); backend token issuance not in this repo (Sleek API / `sleek-back` or equivalent — Unknown exact service name from frontend-only evidence) |
| **DB - Collections** | None in `sleek-website`; persistence for tokens handled server-side — Unknown |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which backend service owns `get-single-use-authentication-token-dashboard` and token TTL or audit logging? Exact market gating if any. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `sleek-website`

- `src/views/admin/companies/index.js` — `getCompanyDashboardUrl(company)` returns `` `/dashboard/?cid=${company._id}` ``. `handleViewDashboardClick` runs only when `api.getCustomerWebsiteUrl() !== ""`; calls `api.getAuthenticationTokenForDashboard` with `body: JSON.stringify({ cid: company._id })`, then `window.open(api.getCustomerWebsiteUrl() + getCompanyDashboardUrl(company) + "&sut=" + singleUseToken, "_blank")`. On failure, shows alert including "Failed to get authentication token for dashboard." Table action: `AnchorButton` with `title="View Dashboard"`, `icon="share"`, `onClick` → `handleViewDashboardClick`.
- `src/utils/api.js` — `getCustomerWebsiteUrl()` returns `process.env.CUSTOMER_WEBSITE_URL || ""`. `getAuthenticationTokenForDashboard` `POST`s to `` `${getBaseUrl()}/admin/users/get-single-use-authentication-token-dashboard` ``. `getAuthenticationToken` unwraps `response.data.auth_token` (stores as `user_auth_token`) or returns `response.data.single_use_token` for the caller.
