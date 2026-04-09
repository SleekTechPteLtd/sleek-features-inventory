# Integrate ERPNext reads for Sleekbook workflows

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Integrate ERPNext reads for Sleekbook workflows |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (integrations), Backend services |
| **Business Outcome** | Lets trusted internal callers resolve Sleekbook companies and read or selectively maintain Frappe documents scoped to a company—including user-permission and fiscal-year cases—so downstream accounting automation can run without direct ERPNext UI access. |
| **Entry Point / Surface** | Backend API only (not a product screen): `sleek-erpnext-service` routes under `/frappe-client/*`, gated by `x-sleek-sdet` matching server secret `DELETE_TEST_COM_AUTH` (`FrappeClientAuthGuard`). |
| **Short Description** | Resolves a company by primary identifier via existing ERP company lookup, lists Frappe documents for a Sleekbook company using `frappe.client.get_list` with tailored filters for standard company scoping, **User Permission**, and **Fiscal Year** child rows, fetches single documents via `frappe.client.get`, and supports signed deletes (cancel-first for certain invoices and bank transactions; fiscal year removes a company row via save). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | ERPNext/Frappe HTTP API (`ERPNEXTBASEURL`, `ERPNEXTOKEN`); `ErpnextService.getCompaniesByFilter` (Company resource lookup); downstream accounting workflows that consume company-scoped ERP data; delete path shares HMAC verification with `DELETE_TEST_COM_AUTH` and optional `company_name` for fiscal-year row removal. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | None for these flows—data is read/written through ERPNext; no MongoDB in `FrappeClientService`. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `getListBySleekbookIdentifier` / `get_doc` return axios error payloads on failure instead of always throwing—intentional contract for callers?; env var name `ERPNEXTOKEN` (typo vs TOKEN) is pre-existing. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Auth (`src/guard/frappe-client-auth.guard.ts`)

- All `FrappeClientController` routes use **`FrappeClientAuthGuard`**: requires header **`x-sleek-sdet`**, must equal `process.env.DELETE_TEST_COM_AUTH` (non-empty); otherwise `ForbiddenException` / `UnauthorizedException` / `InternalServerErrorException` if secret unset.

### Controller (`src/erpnext/frappe-client.controller.ts`)

- **GET** `/frappe-client/get_company/:company_primary_identifier` — `get_company` → `getSleekbookCompanyPrimaryIdentifier` (`ApiOperation`: Get company by company primary identifier).
- **GET** `/frappe-client/get_list/:sleekbook_company_identifier` — query `GetListDto` → `getListBySleekbookIdentifier`.
- **GET** `/frappe-client/get_doc/:doctype/:name` — `get_doc`.
- **DELETE** `/frappe-client/delete/:doctype/:name` — query `company_name`, headers `signature`, `x-correlation-id` → `delete` (HMAC-validated in service).

### Service (`src/erpnext/frappe-client.service.ts`)

- **`getSleekbookCompanyPrimaryIdentifier`**: `erpnextService.getCompaniesByFilter(company_primary_identifier, 0, 1)`; 400 if empty.
- **`getListBySleekbookIdentifier`**: builds `filters` for `frappe.client.get_list`:
  - default: `[["company", "=", "<sleekbook id>"]]`;
  - **`User Permission`**: `[["allow", "=", "Company"], ["for_value", "=", "<id>"]]`;
  - **`Fiscal Year`**: `[["Fiscal Year Company", "company", "=", "<id>"]]` (child table field).
  - HTTP **GET** `api/method/frappe.client.get_list?...` with `fields` default `["*"]`, pagination `limit_start` / `limit_page_length` (default 10), `order_by`.
- **`get_doc`**: **GET** `api/method/frappe.client.get?doctype=&name=` → returns `res.data.message`.
- **`delete`**: validates HMAC `signature` (`<hex>.<payload>`) with `crypto.createHmac('sha256', DELETE_TEST_COM_AUTH)` over `${payload}.${company_primary_identifier || name}.${correlation_id}`; for **Purchase Invoice**, **Sales Invoice**, **Bank Transaction** posts `frappe.desk.form.save.cancel` first; for **Fiscal Year** loads doc, filters out `company_primary_identifier` from `companies` table, `frappe.client.save`; else **`frappe.client.delete`**.

### DTOs (`src/erpnext/dto/frappe-client.dto.ts`)

- **`GetListDto`**: `doctype`, optional `fields`, `filters`, `limit_start`, `limit_page_length`, `order_by`.
- **`ErpnextDoc`**, **`ErpnextDocFiscalYear`**, **`ErpnextDocFiscalYearCompany`** — typing for responses; **`ErpnextDocType`** enum includes `User Permission`, `Fiscal Year`, `Purchase Invoice`, `Sales Invoice`, `Bank Transaction`.
