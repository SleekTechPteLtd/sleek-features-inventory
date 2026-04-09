# Submit receipts via WhatsApp

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Submit receipts via WhatsApp |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User (registered WhatsApp sender linked to receipt users in Sleek Back) |
| **Business Outcome** | Clients submit receipt images and metadata through a guided WhatsApp (Twilio Conversations / Dialog) flow so the same forwarding pipeline as email can deliver documents to Receipt Bank or Hubdoc and, when enabled, create document events for bookkeeping. |
| **Entry Point / Surface** | WhatsApp → Twilio Conversations / Dialog Studio tasks calling Sleek Receipts `POST` routes under the Twilio dialogue webhook (e.g. `initial-step`, `fillin-*`, `greetings-*`). |
| **Short Description** | After companies are resolved from the sender’s WhatsApp number, the user uploads images or PDFs, optionally selects a company when several exist, chooses corporate vs expense-claim receipt type, enters a text description, confirms on a summary screen, and the service forwards the package via `forwardEmailViaWhatsapp` (attachments as base64, optional PDF merge and `documentEventService.createDocumentEvent` when tenant document submission is on). Session expiry and exit via `0` are supported. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Sleek Back API (`getDetailsViaPhoneNumber`, receipt user lookup); `UserDetailService.getReceiptUserByWhatsappAndCompanyId`; `emailForwarder.sendToReceiptBankOrHubdoc`; optional `documentEventService.createDocumentEvent` + `imagesToPDFHelper`; Twilio Conversations (`ConversationsService.retrieveMessageDetails`, `sendStandardWhatsappMessage`); optional CMS `sleek_receipts_settings` / `whatsapp_v2_enabled` for thank-you copy; separate inbound **Messages API** WhatsApp flow under `twilio-whatsapp` routes; Twilio Studio v2 under `routes/twilio.js` `/v2/*` (see `accounting/twilio-v2/submit-receipts-via-whatsapp-studio-flow.md`). |
| **Service / Repository** | sleek-receipts; sleek-back (API) |
| **DB - Collections** | No MongoDB writes in the cited files. In-memory image buffer: `WhatsappDialogueService` (NodeCache keyed by `DialogueSid`). When `tenant.features.document_submission_settings.enabled` is true, `document-event-service` persists document pipeline data (e.g. `DocumentDetailEvent` and related schemas—see that service). `CompanySetting` appears in the broader email-forwarder path, not in the four listed files. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets use Dialog vs v2 vs `twilio-whatsapp` message-receiver; exact Twilio base URL mount for these routes in deployment. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Routing and guards (`src/routes/twilio.js`)

- `POST /initial-step` — `getCompaniesMiddleware`, `setInitialStep` (image capture, retries, company/receipt-type branching).
- `POST /greetings-with-image-selection`, `/greetings-with-receipt-type`, `/greetings-with-description`, `/greetings-with-submission` — `twilioTokenAuth`, controller handlers for collect/listen steps.
- `POST /fillin-company-selection`, `/fillin-image-selection`, `/fillin-receipt-type`, `/fillin-description`, `/fillin-submission` — `twilioTokenAuth`, `authorizationMiddleware` (session expiry, exit on answer `0`), then controller.
- `POST /exit-conversation`, `/session-ended` — cleanup; `sessionEnded` calls `WhatsappDialogueService.dettach(DialogueSid)`.
- `POST /service-activation` — activation code path via `SLEEK_BACK_API.activateServiceViaPhoneAndCode` (registration before submission).

### Controller (`src/controllers/twilio.js`)

- `setInitialStep` — initializes dialogue (`WhatsappDialogueService.initialize`), handles image prompts, numeric company selection, redirects to tasks `greetings-with-image-selection`, `fillin-company-selection`, `fillin-receipt-type`; `addImage` when media present.
- `fillinCompanySelection` — `CompanyGetter.getSelectedCompany`, then receipt-type collect.
- `fillinImageSelection` — `CompanyGetter.getCompaniesByWhatsAppNumber` from `UserIdentifier`; invalid if no companies.
- `fillinReceiptType` — maps `1`/`2` to `receiptConstants.RECEIPT_TYPE` corporate vs personal, then description collect.
- `fillinDescription` — stores `description`, redirects to `greetings-with-submission`.
- `greetingsWithSubmission` — summary with company, receipt type, description.
- `fillinSubmission` — `forwardEmailViaWhatsapp(memoryData, memoryImages)`; optional `SUBMISSION_INPROGRESS` message; failure message on error.

### Service (`src/services/twilio.js`)

- `twilioTokenAuth` — compares `Memory.twilioToken` to `config.twilioToken.authorization`.
- `authorizationMiddleware` — optional 5-minute session expiry (`config.sessionExpiration.enabled`); exit redirect if answer is `0`.
- `getCompaniesMiddleware` — loads companies by WhatsApp number (with retries); user-not-registered and service-unavailable messages.
- `forwardEmailViaWhatsapp` — downloads media URLs to base64 attachments; builds email payload (`sentVia.viaWhatsapp`); `getReceiptUserByWhatsappAndCompanyId`; optional PDF merge + `documentEventService.createDocumentEvent` when document submission enabled; `emailForwarder.sendToReceiptBankOrHubdoc`; outbound WhatsApp thank-you (`WHATSAPP_V2_ENABLED` / CMS toggles message variant).

### Dialogue image cache (`src/services/whatsapp-dialogue.js`)

- Singleton `NodeCache` (600s TTL) stores arrays of image metadata per `DialogueSid`: `initialize`, `addImage`, `getImagesByDialogueSid`, `dettach` on session end.

### Company resolution (`src/companies/get.js`)

- `getCompaniesByWhatsAppNumber` → `SLEEK_BACK_API.getDetailsViaPhoneNumber`, `formatCompanies` grouped by company name.
- `getSelectedCompany(companies, selectedValue)` — index from 1-based user reply.

### Related files (not in FEATURE_LINE but referenced by service)

- `src/messages/email-forwarder.js` — `sendToReceiptBankOrHubdoc` routes to Receipt Bank or Hubdoc addresses from receipt user / company.
- `src/services/document-event-service.js` — document events when tenant flag enabled.
