# Review Zendesk ticket linkage logs

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Review Zendesk ticket linkage logs |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Sleek Admin |
| **Business Outcome** | Compliance and operations staff can see which Zendesk ticket (if any) is linked to a CDD workflow or KYC refresh submission, including errors and manual overrides, to audit escalations and troubleshoot linkage issues. |
| **Entry Point / Surface** | Sleek API: `GET` `/v2/zendesk/logs/reference/{referenceId}` and `GET` `/v2/zendesk/logs/company-user/{companyUserId}` (`app-router.js` mounts the controller at `/v2/zendesk`); `userService.authMiddleware` + `accessControlService.isIn("Sleek Admin")` |
| **Short Description** | Returns stored `ZendeskTicketLogs` for a MongoDB `reference_id` (workflow or KYC history document), or resolves the relevant log for a company user by preferring the latest eligible `kyc_history` entry then falling back to `kyc_workflow`. Responses expose embedded `zendesk_ticket` (ticket id, url, timestamps, error_message, remarks, auto vs manual). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Ticket creation and upsert paths in `zendesk-ticket-service` (`createCDDSubmissionZendeskTicket`, `createKYCRefreshSubmittedZendeskTicket`, manual setters, `updateZendeskLogReferenceIDByCompanyUserID`); `sleek-zendesk-service` for live Zendesk reads elsewhere; CDD/KYC Camunda and compliance workflows that populate logs |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `zendeskticketlogs` (Mongoose model `ZendeskTicketLogs`: `reference_type` workflow \| kyc_history, `reference_id`, `type` cdd_submission \| kyc_refresh_submission, `zendesk_ticket` subdocument); `companyusers` (read: `kyc_workflow`, `kyc_history` for company-user resolution only) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact Sleek Admin screen or client that calls these routes is not identified in-repo; confirm whether `GET` by reference is used for workflow IDs only, KYC history ids only, or both in UI copy. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Router mount** (`app-router.js`): `router.use("/v2/zendesk", require("./controllers-v2/zendesk-controller.js"))`.
- **Controller** (`controllers-v2/zendesk-controller.js`):
  - `getZendeskLogsByReferenceIdHandler` — `GET` `/logs/reference/:referenceId` → `getZendeskLogsByReferenceId(referenceId)`; JSON `{ status: "success", data: logs }`.
  - `getZendeskLogsByCompanyUserIdHandler` — `GET` `/logs/company-user/:companyUserId` → `getZendeskLogsByCompanyUserId(companyUserId)`; same response shape.
  - Both routes: `userService.authMiddleware`, `accessControlService.isIn("Sleek Admin")`.
- **Service** (`services/zendesk-service/zendesk-ticket-service.js`):
  - `getZendeskLogsByReferenceId` — validates non-empty `referenceId` and `mongoose.Types.ObjectId.isValid`; `ZendeskTicketLogs.findOne({ reference_id: referenceId }).sort({ createdAt: -1 }).lean()`.
  - `getZendeskLogsByCompanyUserId` — validates `companyUserId`; loads `CompanyUser.findById(companyUserId).select("kyc_workflow kyc_history")`; uses `resolveLatestEligibleKycHistory` for latest `kyc_history` entry with `is_kyc_refresh_submitted === true`; returns log for that `kyc_history` id via `getZendeskLogsByReferenceId`, else for `kyc_workflow` if present, else `null`.
  - Constants: `ZENDESK_LOG_TYPE` (`cdd_submission`, `kyc_refresh_submission`), `ZENDESK_LOG_REFERENCE_TYPE` (`workflow`, `kyc_history`).
- **Schema** (`schemas/zendesk-ticket-logs.js`): compound-oriented indexes on `reference_type`, `reference_id`, `type`, `zendesk_ticket.ticket_id`.
- **Tests** (`tests/controllers-v2/zendesk-controller.test.js`): route wiring for `getLogsByReferenceId` and `getLogsByCompanyUserId` handlers.
