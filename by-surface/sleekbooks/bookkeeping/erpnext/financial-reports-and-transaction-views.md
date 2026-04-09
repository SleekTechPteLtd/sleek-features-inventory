# Financial reports and transaction views

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Financial reports and transaction views |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User, Bookkeeper, System (jobs and integrations), Backend services |
| **Business Outcome** | Stakeholders can see company financial position and performance for a fiscal year or date range, drill into posted transactions by type, and inspect the chart of accounts—grounding decisions and downstream apps in SleekBooks (ERPNext) data. |
| **Entry Point / Surface** | Backend API consumed by apps and jobs (not a single end-user screen): `sleek-erpnext-service` routes under `/erpnext/*` for BS/PnL queue and retrieval, COA listing, generic reports by type, and transaction lists/counts/detail. One route (`GET /erpnext/get-bank-transactions-count/:type`) uses **`M2MAuthGuard`**; most report and transaction routes have no route-level guard in code—assume gateway or caller auth. |
| **Short Description** | Queues Balance Sheet and Profit and Loss **Prepared Report** runs in ERPNext (with fiscal-year or date-range filters), polls queue status, fetches prepared reports and live query output, saves P&L-related docs via Frappe `savedocs`, lists the full COA for a company UEN, retrieves reports by UEN and report type with period filters, and lists or counts transactions (Sales Invoice, Purchase Invoice, Bank Transaction, Journal Entry, Payment Entry) with optional bank scoping—plus full document load for a transaction by type and id. |
| **Variants / Markets** | Unknown (company resolution uses ERPNext `Company` / `registration_details`; same pattern as other erpnext inventory docs) |
| **Dependencies / Related Flows** | **ERPNext/Frappe** — `frappe.desk.query_report.run`, `background_enqueue_run`, `prepared_report.get_reports_in_queued_state`, `frappe.desk.form.save.savedocs`, `frappe.desk.reportview.get_count`, `frappe.desk.form.load.getdoc`, `/api/resource/*` for Company, Account, and transaction doctypes. **Upstream** — company must exist in ERPNext (UEN → `getCompaniesByFilter`). **Related** — fiscal year and company onboarding (`/get-fy`, company APIs); invoice and bank flows use overlapping transaction types. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | None for these flows—persistence is ERPNext; module registers `Companies` Mongoose schema for other features but report/transaction methods do not use it. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Are `/queue-*` and `/get-*-report-queue` naming and Frappe methods (`get_reports_in_queued_state` vs `background_enqueue_run`) aligned with intended enqueue vs status semantics? `queuePnLReport` passes `end_date` while BS uses `endDate`—confirm client contracts. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller (`src/erpnext/erpnext.controller.ts`)

**Profit and loss — create and queue**

- **POST** `/erpnext/create-profit-loss-report` — `createProfitAndLossReport` → service `createProfitAndLossReport` (`ApiOperation`: Create Profit and Loss Report).
- **POST** `/erpnext/queue-pnl-report` — `queuePnLReport` → `queueReport` with `report_name` **Profit and Loss Statement** (`ApiOperation`: Queue Profit and Loss report for creation). Query: `companyName`, `FYName`, `isFYE`, `startDate`, `end_date`.
- **GET** `/erpnext/get-pnl-report-queue` — `getPnlReportQueue` → `getReportQueue` with same report name (`ApiOperation`: Get Profit and Loss info from Queue).
- **GET** `/erpnext/check-pnl-report` — `checkPnlReport` → `checkPnlReport` (`ApiOperation` summary references Balance Sheet; implementation checks PnL prepared report by name).
- **GET** `/erpnext/get-pnl-report` — `getPnLReport` → `getReportOfCompany(…, 'pnl', …)` (`ApiOperation` summary references Balance Sheet; returns P&L).

**Balance sheet — queue and retrieve**

- **POST** `/erpnext/queue-bs-report` — `queueBSReport` → `queueReport` with **Balance Sheet** (`ApiOperation`: Queue Balace Sheet report for creation).
- **GET** `/erpnext/get-bs-report-queue` — `getBSReportQueue` → `getReportQueue`.
- **GET** `/erpnext/check-bs-report` — `checkBSReport` → `checkBSReport` (GET `Prepared Report` by name).
- **GET** `/erpnext/get-bs-report` — `getBSReport` → `getReportOfCompany(…, 'bs', …)`.

**Chart of accounts and generic reports**

- **GET** `/erpnext/get-coa/:companyUEN` — `getAllCompanyCOA` → `getCompanyCOAByUEN` (`ApiOperation`: Get Existing Company COA List).
- **GET** `/erpnext/get-report/:companyUEN/:reportType` — `getCompanyReportByTypeAndFilters` → `getReportsByNameByCompanyUEN` with query `fiscalYear`, `startDate`, `endDate`, `isFYE` (`ApiOperation`: Get Existing Reports by Type of Company).

**Transactions**

- **GET** `/erpnext/get-transactions/:companyUEN/:type` — `getCompanyTransactionsByTypeAndFilters` → `getTransactionsByCompanyUEN` with `startDate`, `endDate`, `limit`, `offset`, `isCN`, `bankName` (`ApiOperation`: Get Transactions by Type for Company).
- **GET** `/erpnext/get-transactions-count/:companyUEN/:type` — `getCompanyTransactionsCountByTypeAndFilters` → `getTransactionsCountByCompanyUEN`.
- **GET** `/erpnext/get-bank-transactions-count/:type` — `getCompanyTransactionsCountByAccount` → `getTransactionsCountByAccount`; **`@UseGuards(new M2MAuthGuard())`** (`ApiOperation`: Get Transactions Count by bank).
- **GET** `/erpnext/get-transaction/:type` — `getFullTransactionByIDTypeAndFilters` → `getFullTransactionDetailByTypeAndName` with `companyName`, `transactionId` (`ApiOperation`: Get Transaction by ID and Type for Company).

### Service (`src/erpnext/erpnext.service.ts`)

- **`createProfitAndLossReport`** — **POST** `${baseURL}/api/method/frappe.desk.form.save.savedocs` with `doc` JSON and `action: Save`.
- **`checkBSReport`** — **GET** `/api/resource/Prepared Report/{reportname}`.
- **`getReportQueue`** — **GET** `frappe.desk.query_report.background_enqueue_run` with `report_name` and structured `filters` (company, `filter_based_on` FY vs date range, fiscal years, periodicity, etc.).
- **`queueReport`** — **POST** `frappe.core.doctype.prepared_report.prepared_report.get_reports_in_queued_state` with same filter shape.
- **`checkPnlReport`** — **POST** `/api/resource/Prepared Report/{reportname}`.
- **`getReportOfCompany`** — maps `reportType` via **`REPORT_TYPES`** (`erpnext.constants.ts`: `pnl` → Profit and Loss Statement, `bs` → Balance Sheet, etc.); **GET** `frappe.desk.query_report.run` with filters for BS/PnL vs GP-style date ranges.
- **`getCompanyCOAByUEN`** — resolves ERP company via **`getCompaniesByFilter`**, then **`getAllAccounts(erpCompanyName)`**.
- **`getReportsByNameByCompanyUEN`** — UEN → ERP company name, then **`getReportOfCompany`**.
- **`getTransactions` / `getTransactionsCount` / `getTransactionsbyAccountCount`** — Frappe **`reportview.get_count`** and **`/api/resource/{doctype}`** with company and date filters; bank vs posting date field chosen from doctype name.
- **`getTransactionsByCompanyUEN` / `getTransactionsCountByCompanyUEN`** — UEN resolution then **`TRANSACTION_TYPES`** mapping (`sales` → Sales Invoice, `purchase` → Purchase Invoice, `bank` → Bank Transaction, `manualjournal` → Journal Entry, `payment_entry` → Payment Entry).
- **`getFullTransactionDetailByTypeAndName`** — **`frappe.desk.form.load.getdoc`** with resolved doctype and document `name`.

### Constants (`src/erpnext/erpnext.constants.ts`)

- **`REPORT_TYPES`** — `pnl`, `bs`, `gnpnl`, `gp` map to ERPNext report titles.
- **`TRANSACTION_TYPES`** — short keys to Frappe doctype names for listing and detail loads.
