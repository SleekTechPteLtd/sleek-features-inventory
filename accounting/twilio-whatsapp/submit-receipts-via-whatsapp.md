# Submit receipts via WhatsApp

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Submit receipts via WhatsApp |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User (receipt submitter registered for WhatsApp) |
| **Business Outcome** | Receipt submitters send documents through WhatsApp and complete guided steps so submissions become document events and flow into bookkeeping where tenant settings allow. |
| **Entry Point / Surface** | WhatsApp > Sleek Receipts number (inbound Twilio webhook; outbound template replies) |
| **Short Description** | Inbound messages hit `POST /twilio/message-receiver` with session, activation, and media-validation middleware. Redis holds receipt-user session and per-submission state; MongoDB stores WhatsApp conversation rows with step metadata. Users may need number activation (template buttons), then upload one attachment, optionally pick a company by number, choose paid-by-company vs expense claim, and confirm—after which attachments are fetched, optionally merged to PDF, and passed to `documentEventService.createDocumentEvent` when document submission is enabled. Status webhooks update delivery on conversation records. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Twilio (Content templates / `TWILIO_TEMPLATE_MESSAGE`, Messages API); Redis (`TWILIO_REDIS_KEYS` user session, activation session, receipt submission session; expiry can cancel in-flight submission); `CompanyGetter.getCompaniesAndReceiptUsersByWhatsAppNumber` (Sleek Back); `UserDetailService.activateServiceViaPhoneNumber`; `documentEventService.createDocumentEvent` + `imagesToPDFHelper`; `emailForwarderConstant.sentVia.viaWhatsapp`; separate **Twilio Studio / v2** WhatsApp flow in `twilio-v2` routes (see `accounting/twilio-v2/submit-receipts-via-whatsapp-studio-flow.md`). |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `whatsappconversations` (Mongoose model `WhatsappConversation`); document event storage is via `documentEventService` (collection not resolved in these files). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Market-specific rollout and template catalog beyond env-backed Twilio account; exact document-event collection name and Kafka side effects live outside these three files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### HTTP surface (`src/routes/twilio-whatsapp.js`)

- `POST /twilio/send` — `validateDocumentEventAuth()`, `sendMessage` (server-initiated send path).
- `POST /twilio/message-receiver` — `twilio.webhook({ validate: false })`, then `manageSessionMiddleware` → `inputValidationMiddleware` → `checkActivationMiddleware` → `receiveMessage` (inbound user traffic).
- `POST /twilio/callback/status` — `twilio.webhook({ validate: false })`, `statusCallback` (delivery updates).

### Controller (`src/controllers/twilio-whatsapp.controller.js`)

- `sendMessage` — body passed to `twilioWhatsappService.createConversationAndSendMessage`.
- `receiveMessage` — passes Twilio payload plus session fields (`verifiedReceiptUsers`, `pendingVerificationReceiptUsers`, `isSingleCompany`, `selectedCompany`, `isNumberActivated`, `remindActivation`, `invalidInput`) or `sessionError` branch to `receiveMessage` service.
- `statusCallback` — delegates to service `statusCallback`.

### Orchestration and submission (`src/services/twilio-whatsapp.service.js`)

- **Session**: `manageSessionMiddleware` — derives WhatsApp number from `From`, optional `clearSession`, Redis `USER_SESSION`; on miss calls `initializeSessionData` via `CompanyGetter.getCompaniesAndReceiptUsersByWhatsAppNumber`, groups verified vs pending receipt users, sets `isSingleCompany` / `selectedCompany`; `resetAndInitializeSession`; Redis expiry listener can `_handleCancelSubmissionDueToInactivity` and mark conversation cancelled.
- **Activation**: `checkActivationMiddleware` — if only pending users or activation session, sets `isNumberActivated` / `remindActivation` unless Confirm/Maybe Later button.
- **Validation**: `inputValidationMiddleware` — rejects unsupported media MIME extensions into `req.isInvalidInput`.
- **Inbound handling**: `receiveMessage` — `createConversationAndSendMessage` for session/invalid/activation errors; creates row via `createWhatsappConversation`; loads `lastUserConversationWithMedia` for multi-step UX; dispatches `buttonTap`, `mediaUpload` (single media only), `numberInput`, `textInput` via `EventEmitter`.
- **Flow steps**: `onMediaUpload` updates conversation `current_step` / `current_action`, Redis `RECEIPT_SUBMISSION_SESSION` with file queue; templates for choose company vs ask receipt type. `onNumberInput` for multi-company selection. `_templateButtonTapHandlers` for Confirm activation, Maybe Later, Paid by company / me submission (`submitReceiptForSingleCompany` → `_submitDocument`), cancel, view instructions, submitted receipts list.
- **`_submitDocument`**: builds message for `documentEventService.createDocumentEvent` when `tenant.features.document_submission_settings.enabled`, after optional `imagesToPDFHelper`; success/error templates to user.

### Twilio persistence and send (`src/services/twilio-whatsapp-conversations.js`)

- `createWhatsappConversation`, `updateWhatsappConversationBySid`, `updateWhatsappConversationById` — MongoDB CRUD on `WhatsappConversation`.
- `sendTwilioWhatsappMessage` — Twilio client `messages.create` with `contentSid` / `contentVariables`.
- `createConversationAndSendMessage` — resolves `TWILIO_TEMPLATE_MESSAGE[templateType]`, creates outbound conversation row, sends message, updates with `mapWhatsappMessage` result.

### Schema (`src/schemas/whatsapp-conversation.js`)

- Fields include `sid`, direction, addresses, media, `button_text`, `current_step`, `current_action`, `broadcast_message_id`, `message_is_delivered`, etc.
