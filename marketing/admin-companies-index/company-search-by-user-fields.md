# Company search by user fields

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Company search by user fields |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Lets operations staff find companies by how users relate to them (email, allocation, or customer name) and refine the grid by company name and registration number without waiting for a full round-trip on every keystroke for column filters. |
| **Entry Point / Surface** | Sleek Admin > Companies — `/admin/companies/` (`AdminCompaniesView`, sidebar key `companies`) |
| **Short Description** | Toolbar dropdown selects the user-centric search mode (`User Email`, optional `Allocated Users` when resource allocation is enabled, or `Customer Name`). The search field value is sent with `emailType` when the list is refreshed (Enter, search button, or user-type change uses a debounced fetch). Table header inputs filter **Name** and **business registration number** (UEN label from config) with an 800ms debounced `getCompanies` call. Results come from `GET /admin/companies` with query including `email`, `emailType`, `name`, `uen`, pagination, sorting, and other admin filters. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `api.getCompanies` → `getResource` with `admin: true` → `${baseUrl}/admin/companies`; session via `api.getUser()` (unverified users redirected to `/verify/`); company overview/edit links; optional `CreateDraftCompanyButton`; dashboard deep-link via `getAuthenticationTokenForDashboard` |
| **Service / Repository** | `sleek-website` — `src/views/admin/companies/index.js`; `src/utils/api.js` (`getCompanies`, `getResource` admin prefix) |
| **DB - Collections** | Unknown (list/query implemented in API service backing `/admin/companies`, not in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether backend treats `emailType` values with different matching semantics (substring vs exact). `refreshSearch` references `filterStatusSelect` / `filterNameInput` but those elements are not rendered in this component — possible dead code. Which markets expose which filters is tenant/config-driven (e.g. ACRA blocks when `platformConfig.tenant == "sg"`). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/companies/index.js`

- **State:** `userType` default `"User Email"` (lines 58–59); `getCompaniesDebounced = debounce(this.getCompanies, 800)` (line 60).
- **User-type selector:** `<select onChange={this.onUserTypeChange}>` options: `User Email`, conditional `Allocated Users` when `getResourceAllocation` / `resource_allocation` feature flag, `Customer Name` (lines 161–175).
- **Email-side search:** Search `<input onChange={this.handleChangeEmailFilter} onKeyPress={this.handleEnter}` (lines 178–185); `handleChangeEmailFilter` updates `emailFilter` and `page` only (lines 969–972). `handleEnter` / `handleClickSearch` invoke `getCompaniesDebounced` (lines 974–982). `onUserTypeChange` sets `userType` then `getCompaniesDebounced` (lines 984–987).
- **Column filters (debounced):** Name: `handleChangeNameFilter` → `setState({nameFilter, page: 1}, this.getCompaniesDebounced)` (lines 959–962). UEN / BRN: `handleChangeUenFilter` → `uenFilter` + `getCompaniesDebounced` (lines 964–967).
- **Request payload:** `getCompanies` builds `options.query` with `name: nameFilter`, `uen: uenFilter`, `email: emailFilter`, `emailType: userType`, plus `status`, `sub_status`, `clientType`, `company_type`, `record_type`, ACRA filters, `sortBy`, `sortOrder`, `skip` (lines 659–708). Sets `options.admin = true` (line 709).
- **API:** `api.getCompanies(options)` (line 710).

### `src/utils/api.js`

- `getCompanies`: `endpoint = \`${getBaseUrl()}/companies\`` then `getResource(endpoint, options)` (lines 377–382).
- `getResource`: when `options.admin === true`, path becomes `${getBaseUrl()}/admin/companies` (lines 131–133 pattern).

### Related UX (same view, out of scope for this feature line but same page)

- Sortable columns, record type / status / client type filters, SG ACRA filters, pagination, `CreateDraftCompanyButton`, links to company overview or edit.
