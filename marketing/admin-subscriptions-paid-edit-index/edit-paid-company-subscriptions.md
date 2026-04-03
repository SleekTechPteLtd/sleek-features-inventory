# Edit paid company subscriptions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Edit paid company subscriptions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations staff / Sleek Admin (authenticated admin layout; same `company_services` permission patterns as the paid list when editing from there) |
| **Business Outcome** | Paid **company service** rows (subscription line items) stay accurate so billing, renewals, and customer-facing service entitlements match operational reality. |
| **Entry Point / Surface** | **sleek-website** admin: **Subscriptions → Paid** → **Edit** — `/admin/subscriptions/paid/edit/?id=<companyServiceId>`; toolbar back link to `/admin/subscriptions/paid/`. |
| **Short Description** | Loads one company service by `id` query param via **`getCompanyService` with `admin: true`**, fills a form (company id, service type, duration, start date, embedded invoices), shows **read-only invoice blocks** per linked invoice, and saves with **`updateCompanyService`** (`PUT` to admin company-services). Uses shared **`FormSegmentService`** for service type, start date, and duration; **`FormSegmentInvoice`** for display-only invoice fields. |
| **Variants / Markets** | Unknown (no market branching in these views; API host from env / production `api.sleek.sg`). |
| **Dependencies / Related Flows** | **Upstream**: **`viewUtil.fetchDashboardCommonData`** (user, admin `company` / `companies` for layout). **`api.getCompanies`** for `companyList` on mount. **Core**: **`api.getCompanyService`**, **`api.updateCompanyService`** in `utils/api.js` (`putResource` + `admin: true` → `/admin/company-services/...`). **Related**: Paid subscriptions list (`/admin/subscriptions/paid/`), **`admin-services-new`** / other flows that create company services. **Backend** (not in repo): persistence for `company-services` and nested `invoices`. |
| **Service / Repository** | **sleek-website**: `src/views/admin/subscriptions/paid/edit/index.js`, `src/views/admin/services/form-segment-service.js`, `src/views/admin/services/form-segment-invoice.js`, `src/utils/api.js`. |
| **DB - Collections** | **MongoDB** (backend only; not evidenced in sleek-website): **Unknown** — collections behind main API `company-services` routes. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium (edit screen is wired to admin APIs; payload field naming vs form state and company-picker visibility warrant backend/QA confirmation — see Open Questions). |
| **Disposition** | Unknown |
| **Open Questions** | **`makePutServiceRequest`** maps `company_id`, `service`, `duration`, `start_at` from `formValues`, while **`populateCompanyServiceForm`** sets **`company`** (not `company_id`) — confirm whether PUT sends intended company or relies on partial update. **`FormSegmentService`** shows the searchable company control only when **`formType === "new"`**; this edit page does not pass `formType`, so **company is not editable in the UI** here despite being in loaded state — confirm if intentional. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/subscriptions/paid/edit/index.js` (`ServicesEdit`)

- **Mount**: `fetchCommonData` → `viewUtil.fetchDashboardCommonData()`; `fetchCompanyData` → `api.getCompanies()` → `companyList`; `populateCompanyServiceForm` reads `query.id` from URL, calls **`api.getCompanyService(query.id, { admin: true })`**, sets `formValues`: `company` from `companyService.company._id`, `duration`, `service`, `start_at` as `Date`, `invoices` array.
- **Body render**: Requires `this.state.company` from dashboard common data (admin users get a `company` / `companies` via `fetchDashboardCommonData`, including `getRandomCompany` when needed). Renders title **Update Paid Subscription**, form with **`FormSegmentService`** (`companies`, `handleEvent`, `formValues`, `handleOnChangeDate`, `companyList`) and a map of **`FormSegmentInvoice`** per invoice with `disabled={true}`.
- **Submit**: **`makePutServiceRequest`** builds JSON body from keys `company_id`, `service`, `duration`, `start_at` (see Open Questions). **`api.updateCompanyService(query.id, { admin: true, body: JSON.stringify(payload) })`**. Success: alert **Paid company subscription has been updated**, then navigate to **`/admin/subscriptions/paid/`**. Errors: alert with message from thrown API error.
- **Comments in code** explicitly reference **`PUT admin/company-services/:companyServiceId`**.

### `src/views/admin/services/form-segment-service.js` (`FormSegmentService`)

- Renders **service type** select (`secretary`, `director`, `mailroom`), **Start At** (`DateInput` / `handleOnChangeDate`), **Duration (months)** number field.
- **Company** UI: only when **`this.props.formType == "new"`** — searchable **`Select`** over companies from **`api.getCompanies({ query, admin: true })`** keyed by search. Not used as-is on the paid edit page (no `formType="new"`).
- Uses **`FormInputs`** from `components/form-inputs/form-inputs`.

### `src/views/admin/services/form-segment-invoice.js` (`FormSegmentInvoice`)

- Stateless segment: **`FormInputs`** for `title`, `url`, `transaction_id`, `number`, `total_amount`, `status` (processing / done / failed); respects **`props.disabled`** (edit page passes `true` — read-only review).

### `src/utils/api.js`

- **`getResource` / `putResource`**: when **`options.admin === true`**, path is rewritten to include **`/admin`** under **`getBaseUrl()`** (see `getBaseUrl()` for dev vs production).
- **`getCompanyService(companyServiceId, options)`** → `GET ${getBaseUrl()}/company-services/${companyServiceId}` (admin → **`/admin/company-services/:id`**).
- **`updateCompanyService(companyServiceId, options)`** → `PUT` same path (admin → **`PUT /admin/company-services/:id`**).
- **`getCompanies(options)`** → `GET /companies` with optional query string; default `query.is_shareholder = false` unless set.
