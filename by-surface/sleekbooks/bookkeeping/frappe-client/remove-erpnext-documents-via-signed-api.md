# Remove ERPNext documents via signed client API

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Remove ERPNext documents via signed client API |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Lets trusted integrations remove or adjust ERPNext-backed records in a controlled way: invoices and bank activity are cancelled before deletion where required, and fiscal years are updated in place when unlinking a company from year rows instead of deleting the whole fiscal year document. |
| **Entry Point / Surface** | Sleek ERPNext service — HTTP `DELETE /frappe-client/delete/:doctype/:name` (integration callers only; not an end-user app screen) |
| **Short Description** | After route guard and per-request HMAC validation, the service calls ERPNext to cancel Purchase Invoices, Sales Invoices, and Bank Transactions before delete; for Fiscal Year it removes the matching company from the child table and saves; otherwise it calls Frappe client delete. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | ERPNext HTTP API (`frappe.client.get`, `frappe.client.get_list`, `frappe.desk.form.save.cancel`, `frappe.client.save`, `frappe.client.delete`); `ErpnextService` used elsewhere in the module; requires env `ERPNEXTBASEURL`, `ERPNEXTOKEN`, `DELETE_TEST_COM_AUTH` |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | None (service delegates to ERPNext over HTTP; no MongoDB collections in these files) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether `DELETE_TEST_COM_AUTH` env name and `x-sleek-sdet` guard header are legacy naming; which upstream systems call this delete path in production. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Controller** (`erpnext/frappe-client.controller.ts`): `FrappeClientController` is mounted at `frappe-client` and protected by `FrappeClientAuthGuard`. `DELETE /delete/:doctype/:name` passes `company_name` query, `signature` header, and `x-correlation-id` into `FrappeClientService.delete`.
- **Guard** (`guard/frappe-client-auth.guard.ts`): Requires header `x-sleek-sdet` to equal `process.env.DELETE_TEST_COM_AUTH`; otherwise Forbidden / Unauthorized / misconfiguration.
- **Service** (`erpnext/frappe-client.service.ts`): `delete()` parses `signature` as `hex.hmacPayload`, verifies HMAC-SHA256 with `DELETE_TEST_COM_AUTH` over the string built from payload segment, `company_primary_identifier` or `name`, and `correlation_id`. For `Purchase Invoice`, `Sales Invoice`, `Bank Transaction` (`ErpnextDocType`), posts to `frappe.desk.form.save.cancel` before delete (errors logged as warn). For `Fiscal Year`, loads doc via `get_doc`, filters `companies` where `company != company_primary_identifier`, saves via `frappe.client.save`; missing `companies` throws 500. Other doctypes: `frappe.client.delete` with `doctype` and `name`.
- **DTO** (`erpnext/dto/frappe-client.dto.ts`): `ErpnextDocType` enum values used for cancel/delete branching; `ErpnextDocFiscalYear` includes `companies` for fiscal-year row updates.
