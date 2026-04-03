# Manage company statutory registers

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage company statutory registers |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (Sleek Admin — company statutory registers) |
| **Business Outcome** | Corporate statutory books for a client company stay current so compliance and corp-sec operations can rely on accurate officer, charge, share, transfer, debenture, and related register entries. |
| **Entry Point / Surface** | **sleek-website** admin: **`/admin/companies/registers/?cid={companyId}`** — breadcrumbs **Companies > {company name}**; `Registers` React app (`src/views/admin/companies/registers/index.js`), `sidebarActiveMenuItemKey="companies"`. |
| **Short Description** | Admin users open the register list for a company, see each statutory register type with last-updated-from-line-items, and **Edit** to load line items for that type. They **add** new rows via type-specific forms (`forms/index.js` dispatches to nine register forms), **view** tabular line data with date formatting and optional **Notes** in expandable cells (`register-details.js` / `table-cell.js`), and **remove** non-deleted lines after confirmation. Data loads with **`getCompany(..., { admin: true })`** and **`getRegisters`**; edits use **`getRegister`**, **`addRegisterLineItem`** (PUT), and **`deleteRegisterLineItem`**. |
| **Variants / Markets** | **Unknown** — UI is jurisdiction-agnostic; register *types* (e.g. charges, registrable control) align with common-law company register books. Tenant-specific availability of each register is not encoded in these views. |
| **Dependencies / Related Flows** | **Backend API** (host from `getBaseUrl()`, not in repo): `GET/PUT/DELETE` under `/admin/companies/{companyId}/registers/...`. **Related**: **Company edit** corp-sec / governance data ([manage corporate governance and ownership](../admin-companies-edit-index/manage-corporate-governance-and-ownership.md)) — overlapping concepts (officers, nominee directors, shareholding) but this surface is dedicated **statutory register line books**. **Camunda** workflows reference “registers” tasks (incorporation / transfer / share-structure) as operational context, not direct UI coupling here. |
| **Service / Repository** | **sleek-website**: `src/views/admin/companies/registers/index.js`, `company-registers-summary.js`, `register-edit.js`, `register-details.js`, `table-cell.js`, `forms/index.js` and `forms/*.js`; `src/utils/api.js`. **sleek-back** (or equivalent API service): persistence and admin auth for register documents and line items. |
| **DB - Collections** | **Unknown** — MongoDB (or other) collections are not referenced in sleek-website; backend owns register and line-item storage. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which admin roles can access `/admin/companies/registers/` (RBAC on backend). Whether every register type is created for every company or only when applicable. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Routing and shell — `src/views/admin/companies/registers/index.js`

- Webpack entry: `admin/companies/registers/index` → built page **`admin/companies/registers/index.html`** (`webpack/paths.js`, `webpack.common.js`).
- **Load**: `viewUtil.getUser()`; `api.getCompany(query.cid, { admin: true })`; `api.getRegisters(company._id)`.
- Registers are **ordered** for display: `applications_and_allotment`, `officers`, `charges`, `directors_and_shareholding`, `member_and_share_ledger`, `transfers`, `nominee_directors`, `registrable_control`, `debentures` (missing types yield sparse slots from `find`).
- **Summary vs edit**: `CompanyRegistersSummary` lists types and last updated date from last line item’s `updatedAt`; **Edit** sets `register_type` and shows `RegisterEdit`. **Back** refetches `getRegisters`.

### Summary table — `company-registers-summary.js`

- Columns: index, **Register Type** (`titlelize(register.type)`), **Last Updated Date** (from last element of `register.lines` or `-`), **Edit** → `handleClickEdit(event, register.type)`.

### Edit flow — `register-edit.js`

- **Load lines**: `api.getRegister(company._id, register_type)` → state `data` = `response.data.lines`.
- **Add line**: `api.addRegisterLineItem(company._id, registerType, { body: JSON.stringify(payload) })` with error alert via `viewUtil.showResponseErrorAlert`; then refresh with `getRegister`.
- **Delete line**: `api.deleteRegisterLineItem(company._id, register_type, lineItemId)`; then `getRegister`.
- Renders `RegisterDetails` (with `handleClickDelete`) and `FormControl` (with `handleSubmit`, `handleClickBack`).

### Line item grid — `register-details.js`

- Builds dynamic columns from `Object.keys(data[0].data)`; formats many `date_*` and similar keys with `DD/MM/YYYY`; `updated_by` shows `.email`; `notes` uses `TableCell` for long text.
- **Delete**: confirmation `Alert`, then `handleClickDelete` with `lineItem._id`. Rows with `lineItem.deleted === true` get CSS class `deleted` and no remove button.

### Form router — `forms/index.js`

- **`register_type`** switches: `ApplicationsAndAllotment`, `Officers`, `Debentures`, `Charges`, `DirectorsAndShareholding`, `MemberAndShareLedger`, `Transfers`, `NomineeDirectors`, `RegistrableControl` — each in its own file under `forms/`.

### API — `src/utils/api.js`

- `GET ${base}/admin/companies/${companyId}/registers` → **`getRegisters`**
- `GET ${base}/admin/companies/${companyId}/registers/${registerType}` → **`getRegister`**
- `PUT ${base}/admin/companies/${companyId}/registers/${registerType}` → **`addRegisterLineItem`**
- `DELETE ${base}/admin/companies/${companyId}/registers/${registerType}/line/${lineId}` → **`deleteRegisterLineItem`**

### Example form fields — `forms/officers.js`

- Initial fields include `type`, `name_of_officer`, `date_of_appointment`, `date_of_cessation`, `reason_of_cessation`, `notes` — submitted through shared **`handleSubmit`** to **`addRegisterLineItem`**.
