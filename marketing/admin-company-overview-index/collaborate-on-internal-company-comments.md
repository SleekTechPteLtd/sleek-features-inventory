# Collaborate on internal company comments

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Collaborate on internal company comments |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations and internal admin users (Sleek Admin) viewing a client company in admin |
| **Business Outcome** | Staff can leave a shared, timestamped thread on a company record so handoffs, decisions, and follow-ups stay visible without relying on external channels. |
| **Entry Point / Surface** | **sleek-website** admin: **Company overview** at `/admin/company-overview/?cid=<companyId>` — floating **Comment** control (bottom-left) opens **Comments History** popper; optional `openCommentHistory=true` query opens the panel on load (e.g. deep link from **Incomplete orders**). Same Sleek Auditor comment APIs are also used from **Admin > Companies > Edit** and **Subscriptions (new)** table UIs. |
| **Short Description** | Users read paginated internal comments (`skip` query, 20 per page) sorted by `createdAt`, and post new entries. Each post sends `entry_type: "comment"` with `actionBy` (current admin user), `company` snapshot (`_id`, `name`, `uen`), and `text`. The UI shows author initials avatar, name, timestamp, and message body. |
| **Variants / Markets** | Unknown (API host is tenant/env via `API_BASE_URL` / production `api.sleek.sg`; no market split in frontend). |
| **Dependencies / Related Flows** | **Sleek Auditor** HTTP API: `GET` / `PUT` `.../v2/sleek-auditor/api/log/company/:companyId/comment/`. **Related**: company overview bootstrap (`api.getCompany`, etc.); **Paid incomplete orders** links to overview with `openCommentHistory` for comment context. |
| **Service / Repository** | **sleek-website**: `src/views/admin/components/comments/layout.js`, `main.css`; `src/utils/api-sleek-auditor.js` (`getCompanyComments`, `postCompanyComment`). Consumers: `src/views/admin/company-overview/index.js` (`comments()`), `src/views/admin/companies/edit/index.js`, `src/views/admin/subscriptions/new/components/table.js`. **Backend** (not in repo): sleek-auditor service persistence for company comment log. |
| **DB - Collections** | Unknown (stored by sleek-auditor / sleek-back; not defined in sleek-website). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact MongoDB collection(s) and retention for `/v2/sleek-auditor/.../comment/` entries; whether comments are strictly staff-only and audited beyond the log payload. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/utils/api-sleek-auditor.js`

- **`getCompanyComments`**: `GET ${getBaseUrl()}/v2/sleek-auditor/api/log/company/${companyId}/comment/` with optional query string (e.g. `skip=` for pagination).
- **`postCompanyComment`**: `PUT` to the same path via **`putResource`** (note: not the commented-out `postResource`; body supplied by caller as JSON string). Uses **`getDefaultHeaders()`** and standard **`fetch`** pipeline with **`checkResponseIfAuthorized`**.

### `src/views/admin/components/comments/layout.js` (`Comments`)

- **Mount**: **`loadCommentsAndHistory`** → **`getCompanyComments`**; if **`openCommentHistoryByDefault`** (from parent), programmatically opens the popper after mount.
- **Post**: **`handlePostComment`** validates non-empty text, builds payload with **`entry_type`**, **`actionBy`**, **`company`**, **`text`**, calls **`postCompanyComment`**, then reloads **`getCompanyComments`** and clears input; **`commentContainerScrollDown`** scrolls **`#comment-list`** after open/post.
- **Pagination**: **`handleLoadMoreComments`** increments skip by 20, concatenates results, updates load-more label (`Load More...` / `End of Comments...`).
- **UI**: Material-UI **`Popper`** + **`Fade`**; comment count badge on button when **`totalComment >= 1`**.

### `src/views/admin/company-overview/index.js` (`AdminCompanyOverview`)

- Renders **`comments()`** with **`Comments`**: passes **`company`**, **`user`**, **`showErrorDialog`**, **`openCommentHistoryByDefault`**, **`commentContainerScrollDown`** (scroll helper), and handlers (child implements posting via API directly).
- **Query**: **`openCommentHistory`** in URL sets **`openCommentHistoryByDefault: true`** then strips the param (pairs with **Incomplete orders** “view comment” navigation in `paid-incomplete-orders/index.js`).

### `src/views/admin/components/comments/main.css`

- Layout for comment button, popper dimensions (~470×418px), scrollable list, input and send affordance.

### Other call sites (same API)

- **`src/views/admin/companies/edit/index.js`** and **`src/views/admin/subscriptions/new/components/table.js`**: alternate admin surfaces listing **`getCompanyComments`** / **`postCompanyComment`** for the same company-comment capability.
