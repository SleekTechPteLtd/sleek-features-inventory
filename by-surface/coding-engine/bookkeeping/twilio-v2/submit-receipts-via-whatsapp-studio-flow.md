# Submit receipts via WhatsApp (Studio flow)

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Submit receipts via WhatsApp (Twilio Studio) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User (registered receipt submitter via WhatsApp) |
| **Business Outcome** | Receipt images and metadata enter the bookkeeping pipeline (email forwarding to Hubdoc/Receipt Bank and optional document events) without using the web app. |
| **Entry Point / Surface** | WhatsApp > Sleek Receipts channel (Twilio Studio / Autopilot tasks, e.g. `initial-step`, `exit-conversation`, `session-ended`) |
| **Short Description** | Registered users send receipt images or documents through a guided dialogue: company selection when needed, image capture, receipt type and description (flow varies by `whatsapp_v2` flag), then a numeric summary confirmation. Submissions are forwarded via `forwardEmailViaWhatsapp`; bulk-send detection and session/idle rules reduce misuse. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Twilio Studio Autopilot webhooks (`/v2/initial-step`, `/v2/autopilot/on-actions-fetch`, `/v2/error/webhook`); Sleek Back company resolution (`CompanyGetter.getCompaniesByWhatsAppNumber`); `UserDetailService` for receipt user; email forwarding (`emailForwarder.sendToReceiptBankOrHubdoc`); optional `documentEventService.createDocumentEvent` + Kafka `DOCUMENT_CREATED`; Twilio Conversations for post-submit WhatsApp messages |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `documentdetailevents` (via `DocumentDetailEvent.create` when tenant `document_submission_settings` enabled); dialogue image state is **in-process NodeCache** (`WhatsappDialogueService`), not MongoDB |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact market rollout for `whatsapp_v2` / templates toggles (env + CMS `sleek_receipts_settings`) not determined from these files alone. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Routes and HTTP surface (`src/routes/twilio.js`)

- `POST /v2/initial-step` — `TwilioService.getCompaniesMiddleware`, `TwilioV2Controller.setInitialStep`
- `POST /v2/service-activation` — same middleware + `setInitialStep`
- `POST /v2/autopilot/on-actions-fetch` — `retryInitialStep`, `getCompaniesMiddleware`, `setInitialStep` (fallback send on failed Autopilot HTTP response)
- `POST /v2/error/webhook` — `onErrorMessage` (502 → user message via Twilio client)

Auth: `getCompaniesMiddleware` does not use `twilioTokenAuth` on these v2 routes; session integrity relies on Twilio memory + `twilioToken` in remembered state for downstream tasks (v1 pattern). `twilioTokenAuth` appears on v1 routes only.

### Core dialogue orchestration (`src/controllers/twilio-v2.js`)

- `setInitialStep`: main state machine — `WhatsappDialogueService.initialize`, reads memory via `TwilioService.getMemoryData`, branches on images, company count, `GREETING_STEPS` / `FILLIN_STEPS`, `whatsapp_v2_enabled` / `WHATSAPP_V2_ENABLED` and CMS `whatsapp_templates_enabled` (early exit if templates on).
- Exit: `CurrentInput === "0"` → redirect `task://exit-conversation`; thumb emoji + v2 → `replyWithInstructions` (one-at-a-time help link).
- Idle / summary: `resetSummary` after 5 minutes on summary with new file timing; `submitReceipt` on 5-minute timeout; auto-submit path when new image arrives after summary for single-company.
- Bulk: `BULK_UPLOAD_MSG_ENABLED` + `WhatsappDialogueService` image count + `checkTimeLogForBulk` / `logUploadTime` → `bulkUpload` message steering to one-at-a-time.
- Finish: `TwilioV2FillinController.fillinSubmission` on finish / multi-company options.
- `exitConversation`, `sessionEnded` — user-facing end messages; `sessionEnded` after 5 failed attempts on summary options.

### Fill-in steps (`src/controllers/twilio-v2-fillin.js`)

- `fillinCompanySelection`, `fillinImageSelection`, `fillinDescription`, `fillinSubmission` — remember/redirect to `task://initial-step`; submission calls `TwilioService.forwardEmailViaWhatsapp` with optional `NOACKNOWLEDGEMENTMESSAGE` for options 4/5.

### Messaging and company UX (`src/services/twilio-v2.js`)

- `createGreetingsWithSummaryMessage` — v2 copy includes 5-minute default-to-paid-by-company notice and option text (`*1*` paid by company, `*2*` expense claim, `*0*` cancel).
- `createMultipleCompanyMessage` — `collect` with `Twilio.NUMBER` validation, `max_attempts` → `task://session-ended`.
- `greetingsWithImageSelection` — prompt to send images, `listen` to `initial-step`.

### Forwarding into accounting (`src/services/twilio.js`)

- `forwardEmailViaWhatsapp`: loads attachments from media URLs, builds `emailMessage` (sender, receipt type, company, description HTML, `sentVia.viaWhatsapp`), `UserDetailService.getReceiptUserByWhatsappAndCompanyId`; if `document_submission_settings.enabled`, `imagesToPDFHelper`, `documentEventService.createDocumentEvent`, then `emailForwarder.sendToReceiptBankOrHubdoc`; success → `ConversationsService.sendStandardWhatsappMessage` with v2 thank-you copy (`createThankYouMsgAfterWhatsAppSubmission`) or `TwilioConstants.MESSAGES.SUBMISSION_SENT`.
- `getCompaniesMiddleware`: session expiry message; retries `CompanyGetter.getCompaniesByWhatsAppNumber`; unregistered / service-down messages.
- `authorizationMiddleware` / `isSessionExpired`: optional `sessionExpiration` config redirect to `exit-conversation-by-timeout`.

### Session-scoped image cache (`src/services/whatsapp-dialogue.js`)

- `NodeCache` for images per `DialogueSid` and `lastUploadTimeCache` for bulk time window (`MAX_WAIT_TIME_TO_CHECK_BULK_IN_SEC`); `addImage`, `getImagesByDialogueSid`, `resetImageByDialogueSid`, `dettach`, `isNewFile`, `checkTimeLogForBulk`, `logUploadTime`, `removeUploadTime`.

### Constants and flags

- `FILLIN_STEPS`, `GREETING_STEPS`, `THUMB_EMOJIS` from `src/constants/twilio-constants.js` (imported in `twilio-v2.js`).
- Env: `WHATSAPP_V2_ENABLED`, `BULK_UPLOAD_MSG_ENABLED`, `WHATSAPP_TEMPLATES_ENABLED`, `USE_SUBMISSION_WITH_INPROGRESS_NOTIFICATION`, `RECEIPTS_ACCOUNT_SID` / `RECEIPTS_ACCOUNT_AUTH_TOKEN` (Twilio client for error webhook).
