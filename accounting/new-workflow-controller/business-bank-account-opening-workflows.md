# Business bank account opening workflows

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Business bank account opening workflows |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (authenticated admin with `manage_workflows` read/write) |
| **Business Outcome** | Internal operators can start and move bank-account opening and bank-appointment processes forward so client companies complete payment, confirmations, and scheduling steps while Sleek persists state, notifies stakeholders, and updates bank-request records. |
| **Entry Point / Surface** | Sleek admin / operations tooling that mounts `new-workflow-controller` routes — **Bank account opening:** `POST /api/tasks/bankaccountopening/start`, `POST /api/tasks/bankaccountopening/:processId/:taskName/:taskId`. **Bank account opening appointment:** `POST /api/tasks/bankaccountopeningappointment/start`. All require `userService.authMiddleware` and `accessControlService.can("manage_workflows", "edit")` for POST routes. |
| **Short Description** | **Opening:** Starts the `bankaccountopening` workflow in the external Sleek WFE (`sleekWfeBaseUrl`), persists `company_workflow_data` to `CompanyWorkflow`, auto-assigns non-system tasks to the company’s `css-in-charge` resource user, hides the company bank-account widget flag, and triggers zipping of company files and notifications. Task actions forward approvals to WFE for `pending_payment`, `appointment_details`, `bank_account_confirmation`, and `pending_customer_completion`; approved steps run Mongo updates on `CompanyOpenBankAccount` status via store commands. **Appointment:** Starts `bankaccountopeningappointment` in WFE, saves workflow data, and emails selected bankers (mailer template `BANK_ACCOUNT_OPENING_REQUEST_COMPLETE`) with meeting and attendee details, then marks the open-bank-account record completed. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Sleek WFE** — process/task lifecycle (`/workflow/api/tasks/.../start/` and task POSTs). **Mailer** — `mailerVendor` for appointment completion emails. **Related:** `zip-files-and-send-notifications` (document zip and ops notifications on opening start); `Company` / `CompanyOpenBankAccount` product state; shared workflow routes in the same controller (`getProcessSavedData`, `updateProcessSavedData`, task assignment, reset-task). Client-facing business banking eligibility and SBA flows live under other controllers (e.g. company-controller) but are not invoked by these handlers. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companyworkflows` — `CompanyWorkflow` (`doUpdateProcessSavedData`, lookups by `workflow_process_id`); `companyopenbankaccounts` — `CompanyOpenBankAccount` (`has_started_progress` updates); `companies` — `Company` (`is_open_bank_account_widget_show` on start); `companyresourceusers`, `resourceallocationroles` — auto-assignment to `css-in-charge`; `users` — assignee and requestor resolution for emails. Zip/notification side effects may also touch `companyusers`, `files` (see `zip-files-and-send-notifications`). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Regional scope of bank-account opening (not stated in these files). Exact WFE task graph and SLA are defined in WFE, not in sleek-back. Whether `zipFilesAndSendNotificationsCommand` failure blocks workflow start is not explicit (errors logged in handlers). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/admin/new-workflow-controller.js`

- **`POST /api/tasks/bankaccountopening/start`** → `bankAccountOpening.start` — `authMiddleware`, `can("manage_workflows", "edit")`.
- **`POST /api/tasks/bankaccountopening/:processId/:taskName/:taskId`** → `bankAccountOpening.taskAction` — same guards.
- **`POST /api/tasks/bankaccountopeningappointment/start`** → `bankAccountOpeningAppointment.start` — same guards.

### `controllers-v2/handlers/workflow/bank-account-opening.js`

- **`start`** — `postResource` to `${config.sleekWfeBaseUrl}/workflow/api/tasks/bankaccountopening/start/` with `company_id`, `company_name`, `company_user_id`, `company_user_name`, `price`, `payment_status`; then `startSideEffect`: `autoAssignProcessAndTask` (loads `ResourceAllocationRole` type `css-in-charge`, `CompanyResourceUser` for company, `getTasksCommand`, `assignTaskCommand` for non-system tasks), `doUpdateProcessSavedData` with `company_workflow_data`, `hideCompanyBankAccountWidget`, `zipFilesAndSendNotificationsCommand.execute`.
- **`taskAction`** — maps `taskName` to WFE payload keys (`pending_payment` → `payment_status`; `appointment_details` → `appointment_details_approved`; `bank_account_confirmation` → `bank_account_confirmation_approved`; `pending_customer_completion` → `pending_customer_completion_approved`); posts to WFE; on `pending_customer_completion` approved calls `startSuccessProcess`; on `bank_account_confirmation` approved calls `startBankAccountConfirmationApproved`.

### `controllers-v2/handlers/workflow/bank-account-opening-appointment.js`

- **`start`** — `postResource` to `${config.sleekWfeBaseUrl}/workflow/api/tasks/bankaccountopeningappointment/start/` with `company_id`, `company_name`, `company_user_id`, `company_user_name`; `startSideEffect`: `doUpdateProcessSavedData`, `sendAppointmentEmailToSelectedBankers` from `store-commands/workflow/bank-account-opening-appointment/bank-account-opening-appointment`.

### `store-commands/workflow/bank-account-opening/bank-account-opening.js`

- **`startSuccessProcess`** / **`startBankAccountConfirmationApproved`** — `CompanyWorkflow.findOne({ workflow_process_id })`, `CompanyOpenBankAccount.findOne` by `data.request_information.open_bank_account_id`, updates `has_started_progress` per `COMPANY_OPEN_BANK_ACCOUNT_STATUS`.
- **`hideCompanyBankAccountWidget`** — `Company.updateOne` sets `is_open_bank_account_widget_show: false`.

### `store-commands/workflow/bank-account-opening-appointment/bank-account-opening-appointment.js`

- **`sendAppointmentEmailToSelectedBankers`** — loads `Company`, `CompanyOpenBankAccount` with `selected.attendees` populated; per selected bank, `mailerVendor.sendEmail` template `config.mailer.templates.BANK_ACCOUNT_OPENING_REQUEST_COMPLETE`, CC from `config.notification.emails` plus optional `bank_cc_list`; sets `has_started_progress` to `COMPLETED` after sends.

### `store-commands/workflow/common/workflow-processes.js`

- **`doUpdateProcessSavedData`** — reads/writes `CompanyWorkflow` by company and process id (supports `workflow_process_id` or `business_key`).
