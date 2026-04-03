# File ECI and Form C-S and finalize the assessment

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | File ECI and Form C-S and finalize the assessment |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (accountant / tax operator using the CIT workflow) |
| **Business Outcome** | Singapore corporate income tax filings for a year of assessment are submitted to IRAS (ECI and Form C-S paths), acknowledgements are captured, notices of assessment are reviewed and shared with the client, and payment follow-up is recorded so the YA workflow can close. |
| **Entry Point / Surface** | **Sleek App (CIT)** — route `/computation/:companyId/:ya`, reached from the dashboard when opening a company’s tax computation for a given year of assessment; steps appear in the computation task stepper (ECI, Form C-S / dormant Form C-S, NoA, completion). |
| **Short Description** | Operators complete Estimated Chargeable Income (ECI) with optional express path, bot or manual IRAS submission and acknowledgement retrieval, and may skip ECI when revenue and ECI are below configured thresholds. They then complete Form C-S (Parts A–D) or dormant Form C-S with manual acknowledgement upload. Notice-of-assessment flows support emailing documents to the client, objecting via IRAS, marking tax as paid, and payment reminders. A completion screen ends the submission. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | **Backend API** (sleek-cit-back via `customAxiosInstance`): `GET/POST /accounting-flow/tasks`, `GET /accounting-companies`, `GET /accounting-info`, `GET/POST /questionaire`, `GET eci/estimated-income-tax/...`, `POST /eci-filling/bot`, `POST /files/{companyId}/{ya}`, `GET/POST /form-cs`, `GET/POST /dormant-form-cs`, `POST /eci/send-email`, `POST /eci/send-reminder-email`, `POST /form-cs/send-reminder-email`, `updateFYEInfo` (sleek-cit-back service). **Upstream**: data sync, questionnaire, summary steps in the same computation flow. **External**: IRAS (mytax, filing bot, acknowledgements). |
| **Service / Repository** | sleek-cit-ui, sleek-cit-back (API and FYE updates) |
| **DB - Collections** | Unknown — MongoDB or other persistence is handled by sleek-cit-back; this UI only calls REST endpoints. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether dormant Form C-S and standard Form C-S are mutually exclusive branches is determined by server-driven `accounting-flow` task steps, not fully visible in these components alone. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/components/computation-steps/eci/index.js` (ECI)

- **FYE / YA display**: `calculateFYEInfo`, `calculateFYEAfterIncorporation`; `updateFYEInfo` with step key `"file-eci"` for first-year-of-assessment, ECI, estimated tax, tax scheme.
- **Tax estimate**: `GET eci/estimated-income-tax/{taxType}/{eciAmount}`; `getTaxCalulationDetails` persists ECI and estimated tax via `updateFYEInfo`.
- **Questionnaire / express**: `GET /questionaire/{companyId}/{ya}`; ECI express path — `POST /questionaire/...` with `revenue`, `taxScheme`, `yearOfAssessment`, then `updateFYEInfo` and `onStepNext`.
- **Bot vs manual**: `getAccountingFlow` → `GET /accounting-info/{companyId}/{ya}` reads `eci_filling_bot_status`, `eci_filling_bot_message`, ECI fields; `triggerBot` → `POST /eci-filling/bot/{companyId}/{ya}?tag=eci-filling&action=...`; `UploadCard` for manual acknowledgement (`tag` `eci-filling`, `type` `eci`, `section` `file-eci`); `DocumentCard` lists submitted files when bot status is completed.
- **Skip ECI**: `SkipECIDialog` when `ecivalue <= 0` and revenue below `MAXIMUM_REVENUE_TO_SKIP_ECI`; `onStepNext(true)`.

### `src/components/computation-steps/eci/noa/index.js` (ECI Notice of Assessment)

- **`GET /accounting-info/{companyId}/{ya}`** for `eci_noa_details`, `is_send_email_noa`, `is_mark_as_paid_noa`, `paid_date`, `reminder_date`.
- **`POST /eci/send-email/{companyId}/{ya}`** with tax amounts, due date, reference, pay slip, `file_ids` (filters PS- files when tax ≤ 10).
- **`POST /eci/send-reminder-email/{companyId}/{ya}`**; 48h cooldown enforced in UI.
- **`updateFYEInfo`** for `is_mark_as_paid_noa`, `paid_date`.
- **`DocumentCard`** `fileTag` `eci-filling`, `section` `eci-payment`; `ObjectNOADialog` for IRAS objections; `NOASubmit` when `heading === "Confirmation"`.

### `src/components/computation-steps/form-ccs/index.js` (Form C-S)

- **`FormCCS`**: `GET /form-cs/{companyId}/{ya}?isCategorised=true`; `POST` with `accountantId`, `formCSData`, optional `section`; accordion Parts A–C with `PartA`/`PartB`/`PartC` and section keys (`file-formcs-parta`, etc.). `FormPrefillSection` gates next. `TransitionButtons` → Review.
- **`FormCSConfirmation`**: read-only Parts A–C + `PartD`; **`FormSubmitSection`** drives submission success before Next; `GET/POST` same form-cs routes.

### `src/components/computation-steps/form-ccs/noa/index.js` (Form C-S NoA)

- **`GET /accounting-info/{companyId}/{ya}`** for `formcs_noa_details`, `is_send_email_formcs_noa`, `is_mark_as_paid_formcs_noa`, `formcs_paid_date`, `formcs_reminder_date`.
- **`POST /eci/send-email/{companyId}/{ya}?tag=form-cs-filling`** for client email with NoA documents.
- **`POST /form-cs/send-reminder-email/{companyId}/{ya}?tag=form-cs-filling`** for reminders.
- **`updateFYEInfo`** with `is_mark_as_paid_formcs_noa`, `formcs_paid_date`.
- **`DocumentCard`** `fileTag` `form-cs-filling`, `section` `formcs-payment`; `NOASubmit` with `tag` `form-cs-noa` for confirmation step.

### `src/components/computation-steps/dormant-formcs/index.js`

- **`GET /dormant-form-cs/{companyId}/{ya}`**, **`POST /dormant-form-cs/{companyId}/{ya}`** with `formCSData`, `section`.
- Dormant questionnaires (read-only selects) and `unutilised_*` loss/donation fields.
- **`UploadCard`** manual acknowledgement: `tag` `form-cs-filling`, `section` `file-formcs`; gates Next until success.

### `src/components/computation-steps/completed/index.js`

- Completion copy and **`navigate("/")`** to dashboard via `TransitionButtons` with `dashboard={true}`.

### `src/context-providers/computation.provider.js`

- **`GET /accounting-flow/tasks/{companyId}/{ya}`** for step list; **`POST /accounting-flow/tasks/...`** advances `current_step`; optional `eciConfirm` / `formcsConfirm` steps filtered when `eciConfirmation` / `formCSConfirmation` flags are set.
