# Open customer dashboard as company

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Open customer dashboard as company |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Lets operations staff open the client’s customer website dashboard in the correct company context so they can support or verify the experience without sharing long-lived client credentials. |
| **Entry Point / Surface** | Sleek CMS Admin **Companies** list (`/admin/companies/`) — per-company row **View Dashboard** (share icon, tooltip "View", title "View Dashboard") |
| **Short Description** | From the companies table, requests a single-use dashboard token for the selected company (`cid`), then opens a new tab on the customer site at `/dashboard/` with `cid` and `sut` query parameters. No-op if `CUSTOMER_WEBSITE_URL` is unset. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Customer site:** `CUSTOMER_WEBSITE_URL` (see `getCustomerWebsiteUrl()`). **API:** `POST {API_BASE_URL}/admin/users/get-single-use-authentication-token-dashboard` with JSON body `{ cid }`; `getAuthenticationToken` returns `data.single_use_token` or stores `data.auth_token` as `user_auth_token`. **Same pattern** may appear on company overview (`src/views/admin/company-overview/index.js`). Customer app must accept `sut` to establish session. |
| **Service / Repository** | `sleek-website` (admin UI); token issuance and persistence live in the main API backend (not in this repo) |
| **DB - Collections** | None in `sleek-website`; token storage and audit are server-side — Unknown |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Backend owner of `get-single-use-authentication-token-dashboard`, token TTL, and audit logging. Relationship to inventory doc `open-customer-dashboard-as-user.md` (same code path — merge or keep one canonical name?). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `sleek-website`

- `src/views/admin/companies/index.js` — `getCompanyDashboardUrl(company)` returns `` `/dashboard/?cid=${company._id}` ``. `handleViewDashboardClick` runs only when `api.getCustomerWebsiteUrl() !== ""`; calls `api.getAuthenticationTokenForDashboard` with `body: JSON.stringify({ cid: company._id })`, then `` window.open(api.getCustomerWebsiteUrl() + that.getCompanyDashboardUrl(company) + "&sut=" + singleUseToken, "_blank") ``. On failure, alert text includes "Failed to get authentication token for dashboard." Row action: `AnchorButton` with `icon="share"`, `title="View Dashboard"`, `onClick` → `handleViewDashboardClick`.
- `src/utils/api.js` — `getCustomerWebsiteUrl()` reads `process.env.CUSTOMER_WEBSITE_URL || ""`. `getAuthenticationTokenForDashboard` posts to `` `${getBaseUrl()}/admin/users/get-single-use-authentication-token-dashboard` `` via `getAuthenticationToken`, which returns `response.data.single_use_token` or persists `response.data.auth_token` to `store` as `user_auth_token`.
