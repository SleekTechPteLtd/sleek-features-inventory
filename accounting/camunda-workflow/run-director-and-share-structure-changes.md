# Run director and share-structure change workflows

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Run director and share-structure change workflows |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Company user (authenticated; starts workflows and pending-payment records); Operations / Corp Sec (completes Camunda human tasks); system (manual payment handler starts flows after invoice match) |
| **Business Outcome** | Clients progress statutory director changes and share-structure amendments end-to-end—covering resignation, appointment, combined change (including nominee director), and cap-table updates—while keeping Sleek records, registers, and filings aligned with the process. |
| **Entry Point / Surface** | Sleek Back HTTP API under `/v2/sleek-workflow` (see `app-router.js`). Representative paths: `POST /resignation-of-director/start`, `POST /resignation-of-director/:taskId/:taskName`; `POST /appointment-of-director/start`, `POST /appointment-of-director/:taskId/:taskName`, `POST /appointment-of-nominee-director/pending-request`; `POST /change-of-director/start`, `POST /change-of-director/:taskId/:taskName`, `POST /change-of-director/pending-request`; `POST /amend-company-share-structure/start`, `POST /amend-company-share-structure/:taskId/:taskName`, `POST /amend-company-share-structure/pending-request`, `GET /amend-company-share-structure/:business_key/:share_item_key`. All use `userService.authMiddleware` on POST/GET (`controllers-v2/camunda-workflow.js`). |
| **Short Description** | Starts Camunda Pilot BPMN processes for director resignation, appointment, change-of-director, and amend share structure; persists `CompanyWorkflow` (and `PendingCompanyWorkflow` when payment is pending), completes tasks via Pilot `complete-task` APIs, runs store-command side effects (emails, director date updates, nominee assignment, main-POC reassignment), optional `autoAllocateStaff` for KYC roles, and—for share structure—assigns Camunda tasks to `cs-in-charge` and can export cap-table Excel from workflow payload. |
| **Variants / Markets** | SG (task names and completion hooks reference ACRA, registers, Form 45, nominee director artefacts) |
| **Dependencies / Related Flows** | **Sleek Camunda Pilot** (`config.sleekCamundaPilotBaseApiUrl`) start and complete-task endpoints per workflow; **`company-user-service`** (nominee director lookup/assign, main POC reassignment); **`company-resource-user/company-resource-user-service`** (`autoAllocateStaff`); **`camunda-workflow-assignee-service`** (resolve Camunda user for `cs-in-charge` on amend share structure); store-commands under `store-commands/workflow-camunda/{resignation,appointment,change-of-director,amend-company-share-structure}/`; **`workflow-manual-payment-handler`** calls `startAppointmentOfNomineeDirector` and `startChangeOfDirectorForManualPayment` when a paid invoice matches a pending workflow (Xero invoice metadata on external payment payload). Legacy WFE handlers under `controllers-v2/handlers/workflow/*` are a separate stack for some flows. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companyworkflows`, `pendingcompanyworkflows`; reads/writes **`CompanyUser`** when assigning nominee directors or resolving existing ND (`appointment-of-director.js`, `change-of-director.js`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `startAmendCompanyShareStructureForManualPayment` exists on the amend handler but the matching branch in `services/workflow/workflow-manual-payment-handler.js` is commented out—confirm whether amend-from-pending-payment is live via another path. Exact client vs internal-only usage per route is not fully described in these files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/camunda-workflow.js`

- Wires authenticated routes to handlers under `./handlers/camunda-workflow/resignation-of-director`, `appointment-of-director`, `change-of-director`, `amend-company-share-structure` (imports lines 30–33, 41; route blocks lines 132–144, 217–220).

### `controllers-v2/handlers/camunda-workflow/resignation-of-director.js`

- **`start`**: POST body → Camunda Pilot `POST .../resignation-of-director/start?processType=resignation-of-director` via `postResource`; saves **`CompanyWorkflow`** with `workflow_type` `resignation-of-director`, `business_key`, directors, nominee flags; optional **`companyUserService.reAssignMainPOC`** when changing main POC; **`startResignationOfDirectorSideEffects`** → `sendInitialEmails` in store-commands.
- **`taskAction`**: Maps `task_name` (letter_of_resignation, board_resolution, send_resignation_to_acra, register purchases, etc.) to Pilot `POST .../resignation-of-director/complete-task`; on `send_resignation_to_acra` + approved, **`completeRegistrationOfDirector`** loads **`CompanyWorkflow`**, **`sendCompletedRequestEmail`**, **`updateCessationDateAndResignDirector`**.

### `controllers-v2/handlers/camunda-workflow/appointment-of-director.js`

- **`start`**: Validates/assigns nominee via **`validateAndAssignNomineeDirector`** (`getNomineeDirector`, `assignNomineeDirector` with `ND_ENTRY_POINTS.APPOINTMENT_OF_DIRECTOR`); **`initiateAppointmentOfDirectorForCamunda`** → `POST .../appointment-of-director/start?processType=appointment-of-director`; may fetch **`kyc_verification`** task from Pilot; saves **`CompanyWorkflow`** with KYC task metadata; **`autoAllocateStaff`** when tenant flag enabled; **`startAppointmentOfDirectorSideEffects`** (initial emails).
- **`saveProcessDataForPendingRequest`**: Creates **`PendingCompanyWorkflow`** with `workflow_type` **`APPOINTMENT_OF_DIRECTOR`**, invoice/subscription fields, emails customer team for pending payment.
- **`taskAction`**: Completes tasks (assign_a_nominee_director with variables from `CompanyWorkflow`, kyc_verification, form_45, board_resolution, add_new_director_to_acra, registers, nnd/doi/ndsa) via `POST .../appointment-of-director/complete-task`; on **`add_new_director_to_acra`** + approved → **`completeAppointmentOfDirector`** (completion email, **`updateAppointmentDateAndAppointDirector`**); on **`kyc_verification`** + approved → **`sendEmailToCorpSecTeamKycCompleted`**.
- **`startAppointmentOfNomineeDirector`**: Exported for payment completion—checks **`CompanyUser`** for existing ND, may **`assignNomineeDirector`**, starts Camunda, saves **`CompanyWorkflow`** with Xero contact fields from payment payload, side effects, **`PendingCompanyWorkflow.findByIdAndDelete`**.

### `controllers-v2/handlers/camunda-workflow/change-of-director.js`

- **`start`**: Optionally **`assignNomineeDirector`** when appointing ND (`ND_ENTRY_POINTS.CHANGE_OF_DIRECTOR`); **`initiateChangeOfDirectorForCamunda`** → `POST .../change-of-director/start?processType=change-of-director`; saves **`CompanyWorkflow`** with resigning/appointed director payloads, payment fields, main POC reassignment via **`companyUserService.reAssignMainPOC`**; **`startChangeOfDirectorSideEffects`**.
- **`saveProcessedDataForPendingRequest`**: **`PendingCompanyWorkflow`** for **`CHANGE_OF_DIRECTOR`** + pending payment email.
- **`taskAction`**: Completes tasks (KYC, nominee assignment, resign/appoint documents, board resolution, **`update_directors_to_acra`**, registers) via `POST .../change-of-director/complete-task`; on **`update_directors_to_acra`** + approved → **`completeChangeOfDirector`** (**`sendCompletedRequestEmail`**, **`updateChangeDateAndAppointDirector`**, **`updateCessationDateAndResignDirector`**); KYC completion emails corp sec.
- **`startChangeOfDirectorForManualPayment`**: Same pattern as appointment ND—Camunda start, **`CompanyWorkflow`** with PAID + Xero metadata, side effects, delete pending.

### `controllers-v2/handlers/camunda-workflow/amend-company-share-structure.js`

- **`start`**: **`camundaWorkflowAssigneeService.getCamundaUserIdByResourceRole(companyId, "cs-in-charge")`** for Camunda assignee; **`initiateAmendCompanyShareStructureForCamunad`** → `POST .../{AMEND_COMPANY_SHARE_STRUCTURE}/start?processType=...`; saves **`CompanyWorkflow`** with customer app payload, subscription tier flags, price; **`startAmendShareStructureStoreCommands.sendInitialEmails`**; **`autoAllocateStaff`** when enabled.
- **`taskAction`**: Completes tasks (issue_credits, request_review_confirmation, kyc_verification, document_drafting_circulation, acra_filing, update_registers, purchase_electronic_register_of_members) via Pilot complete-task; on approved **`purchase_electronic_register_of_members`** → **`sendShareTransactionRequestEmail`**; on **`acra_filing`** → **`updateDatesShareholder`**, **`sendEmailCompleteAmendShareStructure`**.
- **`saveProcessedDataForPendingRequest`**: **`PendingCompanyWorkflow`** for amend workflow + pending payment email.
- **`startAmendCompanyShareStructureForManualPayment`**: Rebuilds assignee, starts Camunda, merges pending data + Xero contact into **`CompanyWorkflow`**, initial emails, removes pending record.
- **`generateCSVOfCompanyShareItem`**: Loads **`CompanyWorkflow`** by `business_key`, streams Excel via **`generateExcelAmendShareStructureCommands.createWorkbook`**.

### `services/workflow/workflow-manual-payment-handler.js`

- On invoice match to **`PendingCompanyWorkflow`**, switches on `APPOINTMENT_OF_DIRECTOR` → **`camundaAppointmentOfDirector.startAppointmentOfNomineeDirector`**, `CHANGE_OF_DIRECTOR` → **`camundaChangeOfDirector.startChangeOfDirectorForManualPayment`** (imports lines 16–17). Amend share structure branch is commented (lines 48–51).

### Schemas

- **`schemas/company-workflow.js`**: Enum includes `appointment-of-director`, `resignation-of-director`, `change-of-director`, `amend-company-share-structure`.
- **`schemas/pending-company-workflow.js`**: Same workflow types for pending rows.
