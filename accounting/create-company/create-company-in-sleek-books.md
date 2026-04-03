# Create company in Sleek Books

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Create company in Sleek Books |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | A new legal entity exists in Sleek Books bookkeeping with the correct chart-of-accounts setup and currency, so downstream accounting and migration work can run against a real company record. |
| **Entry Point / Surface** | xero-sleekbooks-service HTTP API: `POST /create-company` (Swagger tag `create-company`). Callers must send `Authorization` and are validated via Sleek Back `GET /users/me` (`SleekBackAuthGuard`). Optional `app-origin` header defaults to `admin`. |
| **Short Description** | Accepts company master data (name, abbreviation, currency, country, COA template flags, etc.), forwards creation to ERPNext at `{ERPNEXTBASEURL}/erpnext/create-company`, and records success or failure in application logs. HTTP 201 from ERPNext triggers a success log; HTTP 409 is treated as already-created and still logged as success; other errors are logged and propagated. The same service is reused from migration flows with richer task context; the standalone controller passes an empty task context. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **External** — ERPNext (`ERPNEXTBASEURL`). **Auth** — Sleek Back (`SLEEK_BACK_API_BASE_URL`) for back-office identity. **Related** — `CreateCompanyService` is also provided from `migration` and `tasks` modules for automated migration steps; those paths load task metadata from MongoDB via `getLastestMigration` before logging. **Observability** — `AppLoggerService.createLog` for structured company events. |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | `companies` (Mongoose model `Company`; default pluralized collection name — not overridden in schema). Reads by `_id` in `getLastestMigration` when migration/task context includes an id; the standalone `POST /create-company` path does not persist the request body through this flow. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Are country/currency combinations validated beyond ERPNext? Should the controller pass migration/task identifiers so direct API creates always have rich audit context? Is the shared `Company` model name vs migration document usage intentional for operators? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/create-company/create-company.controller.ts`

- **`POST()`** `/create-company` — **`@ApiOperation({ summary: 'Create new Company in Sleek Books' })`**
- **`SleekBackAuthGuard`** — requires `Authorization` header
- **`ValidationPipe({ transform: true })`** — body validated as **`Company`** schema class
- Delegates to **`CreateCompanyService.create(company, {})`** — empty task info for this entry point
- Responds **201** with `{ newCompany }` (service return value; may be ERPNext response or undefined on 409 path)

### `src/create-company/create-company.service.ts`

- **`create(createMigrationDto, taskInfo)`** — logs company payload at info level
- **`getLastestMigration`** — **`migrationModel.findById`** on **`Company`** model when `taskInfo._id` present; merges latest doc for logging context
- **`HttpService.post`** → **`${ERPNEXT_BASE_API}/erpnext/create-company`** with **`getDefaultHeaders()`**
- **201** → sets message to **`COMPANY_SUCCESS`** (`Company Created Successfully`), **`appLoggerService.createLog('success', ...)`** with user/task fields from `taskInfo`
- **409** → same success log path, returns without throwing
- Other errors → **`appLoggerService.createLog('error', ...)`**, rethrows
- **`LoggerService`** context: feature id **`sleekbooks-migration`**

### `src/create-company/schemas/company.schema.ts`

- **`@Schema({ timestamps: true })`** — **`Company`**: `company_name`, `abbr`, `default_currency` (required strings); optional ERP-style flags (`is_group`, `country`, `create_chart_of_accounts_based_on`, inventory flags, `registration_details`, `existing_company`, `owner`)

### Cross-module

- **`CreateCompanyService`** registered in **`create-company.module`**, **`migration.module`**, **`tasks.module`** with **`CompanySchema`** — migration/tasks flows inject the same service with populated `taskInfo`
