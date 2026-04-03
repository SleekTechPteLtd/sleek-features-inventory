# Send WhatsApp messages to clients

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Send WhatsApp messages to clients |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (authenticated backend services and internal Sleek Receipts flows; clients receive messages only) |
| **Business Outcome** | Clients get timely, consistent WhatsApp notifications and confirmations aligned with bookkeeping workflows (including receipt submission and activation), with sends logged and delivery tracked. |
| **Entry Point / Surface** | **Server-to-server:** `POST /twilio/send` on Sleek Receipts, guarded by `Authorization` header matching `SLEEK_RECEIPTS_TOKEN` (`validateDocumentEventAuth`). **Internal:** `createConversationAndSendMessage` is also invoked from the Twilio inbound webhook pipeline (`receiveMessage`) and from other routes (e.g. external activation flows) — not an end-user Sleek App screen. |
| **Short Description** | Creates a MongoDB row for each outbound send, resolves Twilio Content template configuration (`TWILIO_TEMPLATE_MESSAGE` / `templateType` and optional `templateParams`), sends via Twilio `messages.create` with retry, then persists Twilio message metadata on the conversation record. Delivery status is updated from Twilio status callbacks. The same templated send helper powers both trusted API-triggered notifications and automated replies inside the WhatsApp receipt workflow. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Twilio:** WhatsApp sender (`RECEIPTS_ACCOUNT_VALID_SENDER_TEMPLATES`), Content template SIDs and variables from `TWILIO_TEMPLATE_MESSAGE`. **Inbound webhooks:** `POST /twilio/message-receiver`, `POST /twilio/callback/status` (no Bearer token — Twilio webhook). **Upstream for some flows:** `CompanyGetter` / Sleek Back for session data; `documentEventService` when receipt submission completes after user interaction. **Related inventory:** WhatsApp Studio / log sync under `accounting/twilio-v2` and `accounting/pull-logs-from-twilio` if documented separately. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `whatsappconversations` (Mongoose model `WhatsappConversation`) — create on send; update by `_id` after send and by `sid` on status callback |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Full inventory of callers of `POST /twilio/send` in production; whether Twilio webhook `validate: false` is intentional for all environments and how spoofing is mitigated at the edge. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Routes** — `src/routes/twilio-whatsapp.js`: `POST /twilio/send` → `validateDocumentEventAuth()` → `TwilioWhatsappController.sendMessage`; `POST /twilio/message-receiver` and `POST /twilio/callback/status` use Twilio webhook middleware with `validate: false`.
- **Auth** — `src/middleware/document-event-middleware.js`: `validateDocumentEventAuth` requires `req.headers.authorization === process.env.SLEEK_RECEIPTS_TOKEN`.
- **Controller** — `src/controllers/twilio-whatsapp.controller.js`: `sendMessage` calls `twilioWhatsappService.createConversationAndSendMessage(body)`; `statusCallback` → `twilioWhatsappService.statusCallback(body)`.
- **Conversations / Twilio send** — `src/services/twilio-whatsapp-conversations.js`: `createConversationAndSendMessage({ phoneNumber, templateType, templateParams })` loads `TWILIO_TEMPLATE_MESSAGE[templateType]`, `createWhatsappConversation` (minimal `body`/`from`/`to`), `sendTwilioWhatsappMessage` → `client.messages.create` with `contentSid` and stringified `contentVariables`, `retryFunc` (4 attempts), `updateWhatsappConversationById` with `mapWhatsappMessage(message)`; on failure, updates record with `status: "failed"` and error fields. `sendTwilioWhatsappMessage` uses `RECEIPTS_ACCOUNT_SID_TEMPLATES`, `RECEIPTS_ACCOUNT_AUTH_TOKEN_TEMPLATES`, `RECEIPTS_ACCOUNT_VALID_SENDER_TEMPLATES`.
- **Service (orchestration)** — `src/services/twilio-whatsapp.service.js`: re-exports `createConversationAndSendMessage` for the controller; extensive use of the same helper in `receiveMessage` for templated replies; `statusCallback` calls `updateWhatsappConversationBySid` with delivery flags.
- **Schema** — `src/schemas/whatsapp-conversation.js`: model `WhatsappConversation` fields including `sid`, `status`, `message_is_delivered`, `error_message`, `error_code`, `broadcast_message_id`, etc.
- **Other caller** — `src/routes/external-requests.js`: `createConversationAndSendMessage` for activation template (pattern for non–`/twilio/send` entry points).
