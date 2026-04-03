# Create draft company for onboarding

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Create draft company for onboarding |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators can spin up a draft company record for incorporation or transfer paths without the public funnel, then continue setup in admin company overview. |
| **Entry Point / Surface** | Sleek Admin > Companies (`/admin/companies/`) — primary toolbar **CREATE COMPANY** split button with dropdown (`CreateDraftCompanyButton` next to search; `AdminCompaniesView`, sidebar `companies`) |
| **Short Description** | After platform config loads, staff pick Incorporation and/or Transfer options (tenant-specific: Australia splits transfer into company vs sole trader). The client POSTs a draft `company_data` payload (placeholder name `Draft`, `appOnboardingVersion`, `is_created_by_admin: true`, session token) via the admin API, then the browser opens **Company overview** for the new company in edit mode so onboarding can proceed. |
| **Variants / Markets** | Tenant-driven via `platformConfig.tenant`: **AU** — three menu items and `companyType` SOLE_TRADER vs COMPANY; **GB** — extra England-oriented defaults and flags; other tenants — Incorporation + single Transfer. Not a fixed SG/HK/AU list in UI code beyond those branches. |
| **Dependencies / Related Flows** | `api.createDraftCompany` → `POST /admin/companies/draft-creation` (main API; `postResource` with `admin: true`); auth token `store.get("user_auth_token")`; errors `checkResponseIfAuthorized`; navigation to **Admin company overview** `/admin/company-overview/?cid=…&currentPage=Overview&isEditMode=true&isFromCreateCompany=true`. Upstream: admin session and `getPlatformConfig`. |
| **Service / Repository** | `sleek-website`: `src/views/admin/companies/create-draft-company-button/create-draft-company-button.js`, `src/views/admin/companies/index.js` (embeds button), `src/utils/api.js` (`createDraftCompany`). Backend company persistence: main API (not in this repo). |
| **DB - Collections** | Unknown (company record created by API handling `/admin/companies/draft-creation`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact backend validation and persistence rules per `appOnboardingVersion` and tenant combination; whether all non-AU tenants always expose only two menu items in production. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/companies/create-draft-company-button/create-draft-company-button.js`

- Renders `null` until `platformConfig` is available (lines 12–14).
- **Menu:** `CREATE_COMPANY_OPTIONS` — for `tenant === "au"`: Incorporation, Transfer — Company, Transfer — Sole trader; else Incorporation and Transfer (lines 16–26).
- **`handleCreateCompany`:** builds JSON body with `company_data` (placeholder `name: "Draft"`), sets `appOnboardingVersion` from selection (`Beta-AOT`, `Beta-AOT-SoleTrader`, or `Beta`), `isIncorporationActive` when option is `incorporation`, `isMicroservice: true`, spreads **GB**-specific fields (`tenant === "gb"`) or **AU** `companyType` / `country: "AUS"` (lines 31–92).
- Outer body includes `token` from session store and `is_created_by_admin: true` (lines 38–91).
- **API:** `api.createDraftCompany({ body, admin: true })` (line 93).
- **Redirect:** `window.location.href` to `/admin/company-overview/?cid=${data.id}&currentPage=Overview&isEditMode=true&isFromCreateCompany=true` (lines 94–96).
- **Errors:** `checkResponseIfAuthorized` on failure (lines 98–101).

### `src/views/admin/companies/index.js`

- `CreateDraftCompanyButton` mounted in toolbar with `platformConfig={this.state.platformConfig}` (lines 198–200).

### `src/utils/api.js`

- **`createDraftCompany`:** `POST` to `{getBaseUrl()}/companies/draft-creation` (lines 2206–2209).
- **`postResource`:** with `options.admin === true`, path becomes `{getBaseUrl()}/admin/companies/draft-creation` (lines 147–161).
