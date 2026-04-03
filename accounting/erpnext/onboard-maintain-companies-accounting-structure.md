# Onboard and maintain companies and accounting structure

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Onboard and maintain companies and accounting structure |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, System (integrations), Backend services |
| **Business Outcome** | Client companies exist in SleekBooks (ERPNext) with correct fiscal years, discoverable by UEN, and aligned chart-of-accounts and bank accounts—including bulk setup from BSM—so downstream bookkeeping and banking flows have a consistent accounting skeleton. |
| **Entry Point / Surface** | Backend API consumed by integrations and operations (not a direct user screen): `sleek-erpnext-service` routes under `/erpnext/*` (e.g. company create/update, fiscal year, UEN lookup, COA/bank checks, BSM bulk COA/bank). |
| **Short Description** | Creates and updates **Company** records in ERPNext via REST, attaches or resolves **Fiscal Year** data, lists companies by **registration_details** (UEN-style), and aligns or creates **Account** (COA) and **Bank Account** records—including **M2M**-protected bulk provisioning from BSM that maps bank rows to COA then bank accounts. |
| **Variants / Markets** | SG (UEN-based `registration_details`); other markets Unknown unless confirmed in product. |
| **Dependencies / Related Flows** | ERPNext/Frappe (SleekBooks) REST API (`ERPNEXTBASEURL`, `ERPNEXTOKEN`); BSM (Business Services Management) bank payload for bulk provisioning; SleekAuditor audit logs on COA creation when driven from BSM path; Xero/migration and other flows that consume the same company UEN resolution. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | None in `ErpnextService` for these flows—company master is persisted in ERPNext; module registers `Companies` Mongoose schema for other features but not used here. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether unauthenticated routes are only reachable via internal gateway/network; `get-company-uen/:registerationNumber` param spelling (registration). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller (`src/erpnext/erpnext.controller.ts`)

- **POST** `/erpnext/create-company` — `createCompany` → `createCompanyInErpNext` (`ApiOperation`: Create New Company). No guard.
- **GET** `/erpnext/get-company/:companyName` — `getCompanyByNameFromErpNext`.
- **POST** `/erpnext/add-company-fy` — `addCompanyFY` → `getCompanyAndaddFYEToCompany` (name, start/end FY, UEN) (`ApiOperation`: Add/Update Company Fiscal year).
- **GET** `/erpnext/get-company-uen/:registerationNumber` — `getCompaniesByFilter` with UEN filter (`ApiOperation`: Get Existing Company By UEN).
- **GET** `/erpnext/companies` — paginated company list via `getCompaniesByFilter`.
- **POST** `/erpnext/update-company` — `updateCompanyInErpNext`.
- **GET** `/erpnext/get-accounts/:companyUEN`, `/erpnext/get-bank-accounts/:companyUEN`, `/erpnext/get-coa/:companyUEN` — account/bank/COA lists resolved via UEN → ERP company name.
- **GET** `/erpnext/get-fy` — `getFiscalYear` (`ApiOperation`: Get Existing FY).
- **POST** `/erpnext/check-coa`, `/erpnext/check-bank-account` — `checkCoa`, `checkBankAccount` (align or create).
- **POST** `/erpnext/check-create-coa` — `checkAndCreateCOA` with **`M2MAuthGuard`** (machine-to-machine).
- **POST** `/erpnext/bulk-create-company-coa-bank-accounts-bank-from-bsm` — `bulkCreateCompanyCoaBankAccountsAndBankfromBsm` with **`M2MAuthGuard`** (`ApiOperation`: bulk create COA, bank account and bank from BSM if not exists).

### Service (`src/erpnext/erpnext.service.ts`)

- **createCompanyInErpNext**: `POST` `api/resource/Company`, then `addFYEToCompany` / fiscal year chain.
- **getCompaniesByFilter**: `GET` `api/resource/Company` with optional filters `registration_details` = UEN (empty string = list with pagination).
- **getCompanyAndaddFYEToCompany**: resolves company by UEN via `getCompaniesByFilter` or by name via `getCompany`, then `addFYEToCompany`.
- **getFiscalYear** / **createFiscalYear** / **addFYEToCompany**: `Fiscal Year` doctype.
- **checkCoa** / **checkAndCreateCOA**: lookup by account code, ID, or name; optional `createNewCoa`; BSM path calls `addAuditLogForCOACreatedEvent` → `SleekAuditorService.insertLogsToSleekAuditor` with tags `accounting`, `bsm`, `expnext`, `sleekbooks`.
- **checkBankAccount** / **createNewBankAccount**: find or create **Bank Account** linked to COA name.
- **bulkCreateCompanyCoaBankAccountsAndBankfromBsm**: validates company by `company_uen` via `getCompaniesByFilter`; for each BSM bank row runs `checkAndCreateCOA` (parent `Current Assets`, type `Bank`) then `checkBankAccount`; returns `identifier` → `account_name` mapping.

### Types

- `src/erpnext/dto/erpnext.dto.ts` — `CompanyData`, `CompanyFYData` (includes `uen`).
- `src/erpnext/interface/erpnext.interface.ts` — `BulkCreateCompanyCoaBankAccountsAndBankfromBsmPayload` (`sleek_company_id`, `company_uen`, `bank_accounts[]` with `identifier`, `account_name`, `bank_name`, `account_number`, `currency`).

### External systems

- **ERPNext/Frappe** REST (`baseURL` from `ERPNEXTBASEURL`, `Authorization` token from `ERPNEXTOKEN`).
