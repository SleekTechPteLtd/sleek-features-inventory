# Prepare and review tax computation inputs

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Prepare and review tax computation inputs |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Corporate income tax computation for a year of assessment is grounded in reviewed questionnaires, mapped accounts, and classified transactions so chargeable income matches the business and the chosen tax scheme. |
| **Entry Point / Surface** | Sleek CIT App (authenticated) > Dashboard / company selection > Tax computation workflow at route `/computation/:companyId/:ya` — guided by the task stepper (form type selection through statement summary). |
| **Short Description** | Accountants select the filing form type, complete the materiality and tax-residency questionnaire (including Xero-backed materiality figures), map revenue and expense accounts to tax schedules and chargeability, review and filter transactions by category, then view and adjust the statement summary including the tax exemption scheme before later filing steps. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | **Upstream:** Data sync for accounting data (`/datasync/check-data`, DataSync step); Xero tenant / UEN for questionnaire and COA data. **API:** `sleek-cit-back` (accounting-info, questionaire, coa, transactions, accounting-flow). **Downstream:** ECI and Form C-S filing steps (not part of this capability but sequential in the same flow). |
| **Service / Repository** | sleek-cit-ui, sleek-cit-back |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | MongoDB collections are not visible from the UI repo; confirm product marketing name for the app (e.g. “Sleek CIT”) if inventory naming must match customer-facing copy. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Orchestration and entry

- `src/pages.js` registers the computation page at `/computation/:companyId/:ya` with `requiresAuth: true`.
- `src/components/computation-steps/index.js` (`ComputationSteps`) wires the stepper: **FormSelection** → **Questionaire** → **COA** → **TransactionReview** → **Summary** (plus DataSync before form type, and later ECI/Form CS steps).
- `src/components/computation-core/index.js` wraps the flow in `ComputationProvider`.

### Form type selection

- `src/components/computation-core/form-selection/index.js`: Loads revenue from `GET /accounting-info/:companyId/:ya`; submits `POST /accounting-flow/update-form-type/:companyId/:ya` with `formType` (Form C-S, Form C, dormant); calls `onGetSteps` to refresh task steps. Preselects form type from revenue thresholds ($5M) and express flags.

### Materiality questionnaire and tax scheme

- `src/components/computation-steps/questionaire/index.js`:
  - `GET /questionaire/:companyId/:ya`, `POST /questionaire/:companyId/:ya` with `questionaireData`, `taxScheme` (`startup` | `partial`), `accountantId`.
  - `GET /questionaire/materiality/:companyId/:ya` (Xero materiality).
  - `GET /questionaire/info/:companyId/:ya` (company/exchange rate).
  - `GET /transactions/travel/:companyId/:ya` (travel-related lines for Part 2).
  - `updateFYEInfo` from `services/sleek-cit-back` for tax scheme on FYE (`tax_scheme`).
  - Renders `PartOne`–`PartThree`, `Losses`, conclusion for Partial vs New Startup exemption; `setMaterialityLevel` passed to parent for downstream transaction review.

### Chart of accounts mapping

- `src/components/computation-steps/coa/index.js`:
  - `getCoaByCompanyId` → `GET /coa/accounts/:companyId/:xeroId/:type?search=...`
  - `getCoaSchedulesByType` → `GET /coa/schedules/:type`
  - `updateCoaStatusByCompanyId` → `POST /coa/accounts/:companyId/:xeroId/:type` with `accountantId`, `yearOfAssessment`, account fields including `chargeable_status`, `schedule_type`, `schedule_code`.
  - Tabs for revenue vs expense (`ACCOUNT_TYPE`); sub-steps `coaRevenue` / `coaExpense` via `getCurrentSubStepData`.

### Transaction review

- `src/components/computation-steps/transaction-review/index.js`:
  - `GET /transactions/category/:companyId/:accountType/:ya` (categories + materiality level).
  - `GET /transactions/list/:companyId/:accountType/:ya` with pagination and filters: `searchTerm`, `isDeductible`, `hasDocument`, `currencyType`, `currencyMin`/`currencyMax`, `valid` (reversible).
  - `GET /transactions/export/:companyId/:ya` for export.
  - Revenue uses “Chargeable” vs expenses “Deductible”; `MaterialityOptions` for currency filters.

### Statement summary and tax scheme display

- `src/components/computation-steps/summary/index.js`:
  - `GET /accounting-info/:companyId/:ya` for summary payload and `tax_scheme`.
  - `SummaryTable`, `SummaryStatTile` show YA, basis period, functional currency, tax exemption scheme label (e.g. New Startup vs partial).
  - `updateFYEInfo` / `POST /accounting-info/...` for saved summary fields (losses, credits, carry-forwards, etc.).
  - `exportSummaryPDF` for “DOWNLOAD TAX COMPUTATION”.

### Shared services

- `src/services/sleek-cit-back/index.js`: `getCoaByCompanyId`, `updateCoaStatusByCompanyId`, `getCoaSchedulesByType`, `updateFYEInfo`, `exportSummaryPDF`.

### Auth surface

- All computation routes require authentication (`requiresAuth: true`); actions send `accountantId` / `currentLoggedInuser.email` to the backend.
