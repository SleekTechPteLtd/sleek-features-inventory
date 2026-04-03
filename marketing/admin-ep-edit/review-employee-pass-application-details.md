# Review employee pass application details

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Review employee pass application details |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations user (Sleek admin / staff with Employment Pass admin access) |
| **Business Outcome** | Internal staff can open a single Employment Pass application and read submitted company, applicant, and employee personal data in one place to verify accuracy or support downstream processing (copy/paste out of the tool). |
| **Entry Point / Surface** | **sleek-website** admin: **`/admin/ep/edit?epid=<EP id>`** — `AdminLayout` with `sidebarActiveMenuItemKey="ep"`, breadcrumbs **EP** → current EP `_id`. Not linked from the EP list table in `admin/ep/index.js` (that list opens **Review Form** on the public **`/ep/`** flow); this screen is reached by direct URL or other internal navigation. |
| **Short Description** | Loads one EP record by query `epid` and renders **Application Information** and **Employee Personal Information** in read-only `CopyableInput` fields (company name, applicant email, pass/FIN context, duration, director question, full personal/spouse/travel/address fields). Dates are formatted with `DD/MM/YYYY`; country of birth is resolved via `countries` lookup. No submit or mutation on this page. Unverified users are redirected to `/verify/`. |
| **Variants / Markets** | **SG** (Employment Pass is Singapore-specific). Other tenants: **Unknown** if this screen is hidden or unused. |
| **Dependencies / Related Flows** | **`api.getEp(epId)`** → **`GET ${base}/eps/:id`** (no `admin: true` in `edit.js`, so client does not rewrite to `/admin/eps/...` unless options change elsewhere). **`api.getUser`** for session and email verification gate. Upstream: EP list and creation at **`/admin/ep/`** (`manage-ep-applications`). Applicant-facing flow at **`/ep/`** for form submission. Backend persistence and RBAC: **sleek-back** (not in this repo). |
| **Service / Repository** | **sleek-website**: `src/views/admin/ep/edit.js`, `src/utils/api.js` (`getUser`, `getEp`). **sleek-back**: EP REST API for `/eps/:id` and user linkage. |
| **DB - Collections** | **Unknown** (backend). EP application documents and embedded `data` / `user` fields are not defined in sleek-website. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether **`GET /eps/:id`** without `options.admin` is intentional for this admin screen vs **`GET /admin/eps/:id`**, and how server-side authorization differs. Whether the **Travel Document Upload** row (empty `FormGroup`) was meant to show a file link or is unfinished. How staff typically discover this URL if not linked from the EP index. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/ep/edit.js` (`AdminEpEditView`)

- **Mount**: `domready` → `#root`; **`componentDidMount`**: **`getUser`** then **`getEp`**.
- **Query**: `epid` from `window.location.search` → **`this.state.epId`** (required for **`getEp`**).
- **Layout**: `AdminLayout` with **`hideDrawer={true}`**, **`sidebarActiveMenuItemKey="ep"`**; toolbar breadcrumbs **`/admin/ep/`** (“EP”) → **`ep._id`**.
- **Data**: **`api.getEp(this.state.epId)`** → **`setState({ ep: response.data })`**; fields read from **`ep.data`** and **`ep.user.email`**.
- **Application Information** (`renderApplicationInfo`): read-only **`CopyableInput`** — `company_name`, `applicant_email` (from `ep.user.email`), `employee_previous_fin_or_permit`, `employee_pass_duration`, `employee_sole_proprietor_or_director`.
- **Employee Personal Information** (`renderPersonalInfo`): read-only **`CopyableInput`** for extensive `ep.data` keys (names, sex, marital status, DOB, nationality, Malaysian ID fields, country of birth via **`getCountryName`**, race, religion, spouse fields, travel document fields, Singapore address fields). **`date.formatDate`** for date fields. **Travel Document Upload** row has empty **`FormGroup`**.
- **Auth**: **`getUser`** — if `registered_at` is null, redirect **`/verify/`**; errors via **`checkResponseIfAuthorized`**.

### `src/utils/api.js`

- **`getEp(epId, options)`**: **`GET`** `` `${getBaseUrl()}/eps/${epId}` `` via **`getResource`**. **`options.admin === true`** would rewrite base URL to **`/admin`** (not used by the edit view call site).
- **`getUser`**: used for authenticated admin user and verification gate (see `getUser` implementation elsewhere in this file).

### Related

- **`src/components/copyable-input`**: enables copy-friendly read-only display (imported as **`CopyableInput`**).
- **`src/utils/countries`**: **`find(..., { alpha3Code })`** for **Country of Birth** display name.
