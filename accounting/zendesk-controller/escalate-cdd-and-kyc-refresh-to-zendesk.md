# Escalate CDD and KYC refresh to Zendesk

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Escalate CDD and KYC refresh to Zendesk |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Sleek Admin (HTTP routes); **System** triggers the same service functions from Camunda CDD completion (`complete-task-actions.js`) and from `kyc-refresh-service.js` after KYC refresh submission |
| **Business Outcome** | Compliance receives actionable Zendesk tickets when CDD remediation or KYC refresh work is submitted, with MongoDB-backed linkage to the CDD workflow or the latest submitted `kyc_history` entry; manual ticket IDs can be recorded when automation is wrong or unavailable. |
| **Entry Point / Surface** | **Automated:** Camunda customer-due-diligence task completion → `createCDDSubmissionZendeskTicket(companyId)`; KYC refresh pipeline → `createKYCRefreshSubmittedZendeskTicket(companyUserId)`. **Sleek Admin API** (`app-router.js` mounts controller at `/v2/zendesk`): `POST` `/cdd/form-submitted/create-zendesk-ticket/:companyId`, `POST` `/kyc-refresh/submitted/create-zendesk-ticket/:companyUserId`, `POST` `/cdd/workflow/:workflowId/ticket/:ticketId/set-manual`, `POST` `/kyc-refresh/company-user/:companyUserId/ticket/:ticketId/set-manual` — all with `userService.authMiddleware` and `accessControlService.isIn("Sleek Admin")`. |
| **Short Description** | Creates Zendesk tickets via the Sleek Zendesk HTTP service (compliance group, tags `cdd_refresh`/`compliance` or `kyc_refresh`/`compliance`, HTML body with Sleek Admin company overview links). Upserts `ZendeskTicketLogs` keyed by `reference_type` + `reference_id` + `type` (CDD: workflow; KYC: `kyc_history` id). Enforces eligibility (CDD: form `done`, workflow active, no duplicate success log; KYC: latest `kyc_history` with `is_kyc_refresh_submitted`, duplicate checks against log and embedded ticket id). Manual handlers fetch the ticket from Zendesk, then upsert logs with audit remarks and `is_set_auto: false`. Errors persist to logs with `error_message` when applicable. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Sleek Zendesk** (`SLEEK_ZENDESK_BASE_URL`): `POST /zendesk/create-ticket`; `app-features-util` feature `cdd_refresh` (`value.requester_email`); `config.sleekAdminBaseUrl`; env `ZENDESK_COMPLIANCE_GROUP_ID`; Camunda constants for CDD workflow status; `closeCDDWorkflowZendeskTicket` / `closeKYCRefreshZendeskTicket` (other flows, same module). Related inventory: manage company Zendesk tickets (`getCompanyZendeskTickets`, close by id); review Zendesk ticket linkage logs (`getZendeskLogsByReferenceId`, `getZendeskLogsByCompanyUserId`). |
| **Service / Repository** | sleek-back; external **Sleek Zendesk** service (Zendesk API proxy) |
| **DB - Collections** | `zendeskticketlogs` (upsert/read for linkage and errors); `companies` (`cdd_remediation_workflow`); `companyusers` (owner for CDD requester context; `kyc_history`, `kyc_workflow`, populated `user`/`company` for KYC); `companyworkflows` (CDD workflow `_id`, `workflow_status`, `data.cdd_form_submission.status`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Router mount** (`app-router.js`): `router.use("/v2/zendesk", require("./controllers-v2/zendesk-controller.js"))`.
- **`controllers-v2/zendesk-controller.js`**
  - `POST` `/cdd/form-submitted/create-zendesk-ticket/:companyId` → `createCDDFormSubmissionZendeskTicket` → `createCDDSubmissionZendeskTicket(companyId)`.
  - `POST` `/kyc-refresh/submitted/create-zendesk-ticket/:companyUserId` → `createKYCRefreshSubmissionZendeskTicket` → `createKYCRefreshSubmittedZendeskTicket(companyUserId)`.
  - `POST` `/cdd/workflow/:workflowId/ticket/:ticketId/set-manual` → `setCDDWorkflowZendeskTicketManuallyHandler` → `setCDDWorkflowZendeskTicketManually({ workflowId, ticketId, setByUserEmail })` (`setByUserEmail` from `req.user.email` or `"SYSTEM"`).
  - `POST` `/kyc-refresh/company-user/:companyUserId/ticket/:ticketId/set-manual` → `setKYCRefreshZendeskTicketManuallyHandler` → `setKYCRefreshZendeskTicketManually({ companyUserId, ticketId, setByUserEmail })`.
  - All routes: `userService.authMiddleware`, `accessControlService.isIn("Sleek Admin")`.
- **`services/zendesk-service/zendesk-ticket-service.js`**
  - `upsertZendeskTicketLog` — `ZendeskTicketLogs.findOneAndUpdate` on `{ reference_type, reference_id, type }` with `$set` / `$setOnInsert`.
  - `ZENDESK_LOG_TYPE`: `cdd_submission`, `kyc_refresh_submission`; `ZENDESK_LOG_REFERENCE_TYPE`: `workflow`, `kyc_history`.
  - `getCompanyAndEligibleWorkflow` / `createCDDSubmissionZendeskTicket` — loads `Company`, `CompanyWorkflow` by `cdd_remediation_workflow`; checks `formStatus === "done"` and active CDD workflow status; duplicate guard via `findLatestSuccessfulZendeskTicketLog`; builds payload with compliance requester from `getComplianceRequesterEmail()`, `buildComplianceZendeskGroup()`; `sleekZendeskService.createTicket(payload)`; success/error upsert.
  - `createKYCRefreshSubmittedZendeskTicket` — `CompanyUser.findById` + populate; `resolveLatestEligibleKycHistory` (latest `kyc_history` with `is_kyc_refresh_submitted`); duplicate checks vs log and `latestKycHistoryEntry.zendesk_ticket.ticket_id`; creates ticket and upserts with `reference_type: kyc_history`, `reference_id: kycHistoryId`.
  - `setCDDWorkflowZendeskTicketManually` — validates `CompanyWorkflow`; `getFormattedZendeskTicketById`; upsert CDD log on workflow id.
  - `setKYCRefreshZendeskTicketManually` — resolves latest eligible `kyc_history` id; upsert KYC refresh log on that id.
- **`services/zendesk-service/sleek-zendesk-service.js`**
  - `createTicket` — `axios.post` `${sleekZendeskBaseUrl}/zendesk/create-ticket` with JSON body (same payload shape as ticket service).
- **Automated callers (same service module)**
  - `store-commands/workflow-camunda/customer-due-diligence/complete-task-actions.js` — `createCDDSubmissionZendeskTicket(companyId)` on relevant task completion.
  - `services/kyc-refresh-service.js` — `createKYCRefreshSubmittedZendeskTicket(companyUserId)` after submission path (line ~747 in current tree).
- **Schema** (`schemas/zendesk-ticket-logs.js`): model `ZendeskTicketLogs`; enum `type` / `reference_type`; subdocument `zendesk_ticket` (`ticket_id`, `url`, `createdAt`, `error_message`, `remarks`, `is_set_auto`).
- **Tests** (`tests/services/zendesk-service/zendesk-ticket-service.test.js`, `tests/controllers-v2/zendesk-controller.test.js`): coverage for create and controller wiring.
