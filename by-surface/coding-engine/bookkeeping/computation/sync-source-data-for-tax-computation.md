# Sync source data for tax computation

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync source data for tax computation |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Downstream corporate income tax steps use accounting data (ledger-linked reports, chart of accounts, and transactions) that match the chosen software, period, and year of assessment. |
| **Entry Point / Surface** | Sleek CIT app → company computation flow → **Data Sync** step (`current_step` / workflow includes `dataSync`; route params `companyId`, `ya`) |
| **Short Description** | Operators choose SleekBooks or Xero (when multi-ledger), set the sync window within FYE bounds, then trigger or refresh sync for reports, chart of accounts, and transactions via backend datasync jobs. Optional **Express filing** (Form C-S or ECI) skips sync and uploads files to IRAS instead. Foreign individuals without Singpass can record an IRAS tax reference number (ASGD). FX items are managed in a related card on the same screen. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | Backend `/datasync/*` and `/accounting-flow/*` APIs; `sleek-cit-back` services `getASGDNumber` / `updateASGDNumber`; ledger sources Xero and SleekBooks; subsequent steps (`formType`, summary, etc.) via `ComputationProvider` task flow; optional express filing updates `form_cs_express` / `eci_express` |
| **Service / Repository** | sleek-cit-ui; backend services exposing accounting-flow and datasync (not named in-repo) |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact app shell branding/route prefix for “Sleek CIT” not resolved in these files; MongoDB collections for sync jobs live in backend only. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/components/computation-core/datasync/index.js` (`DataSync`)

- **Workflow context:** `useComputation()` for `companyInfo`, `setCompanyInfo`, `onStepUpdate`, `taskStepsIDs`; `useParams()` for `companyId`, `ya`; `useApp()` for `isExpressEnabled`.
- **Ledger and period:** Radio group SleekBooks (`sb`) vs Xero (`xero`) when `multi_ledger > 1`; date range constrained by `companyInfo.original_dates`; save posts to `POST /accounting-flow/update/:companyId/:ya` with `ledger`, `start_date`, `end_date`, `userId`, `functional_currency`.
- **Three sync domains** (labels): Reports (index 0), Chart of Account (1), Transactions (2). Status UI maps backend statuses (`new`, `inprogress`, `pending`, `completed`, `failed`, `aborted`).
- **List / poll:** `GET /datasync/list/:companyId/report/:ya/all`, `.../coa/...`, `.../transactions/...` — first row drives displayed status.
- **Trigger sync:** `POST /datasync/report/:company_id?role=...`, `POST /datasync/coa/:company_id?role=...`, `POST /datasync/transactions/:company_id?role=...` with `xeroId` (from `xero_tenant_id` or `uen`), `yearOfAssessment` (`ya`), and `functionalCurrency` where applicable.
- **Aggregate:** `checkDataSyncStatus` requires all three `completed` before `onRefreshCheckData`; `reSyncData` / `refreshData` support per-index or `"all"`.
- **Navigation:** `onDataSyncNext` advances via `onStepNext` or `onStepUpdate("formType", true)` depending on step order vs `formType`.
- **Express branch:** When `isExpressEnabled`, renders `FormCSExpressDataSync`; `onExpressFilingSelected` toggles sync/next-button behaviour from `form_cs_express` and `eci_express` on `companyInfo`.
- **Other:** `getASGDNumber` / `updateASGDNumber` from `services/sleek-cit-back`; `FXItemsCard` for FX with `companyId`, `ya`, `ledger`, `functional_currency`.

### `src/components/computation-core/datasync/form-cs-express-datasync.js` (`FormCSExpressDataSync`)

- Checkboxes for Form C-S express and ECI express; mutual exclusion in handlers.
- **Persist:** `POST /accounting-flow/update-express-filing/:companyId/:ya` with `isFormCSExpress`, `isECIExpress`; on success calls `onExpressFilingSelected` and `setCompanyInfo(response.data)`.

### `src/context-providers/computation.provider.js` (`ComputationProvider`)

- Default `currentStep` state `"dataSync"`; loads company via `GET /accounting-companies/:companyId/:ya` and task graph via `GET /accounting-flow/tasks/:companyId/:yearOfAssesment`.
- Exposes `onStepUpdate` → `POST /accounting-flow/tasks/:companyId/:ya` for step transitions; merges `companyInfo` for downstream screens.
