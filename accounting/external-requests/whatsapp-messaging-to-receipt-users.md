# WhatsApp messaging to receipt users

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | WhatsApp messaging to receipt users |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, System (backend integrations calling Sleek Receipts) |
| **Business Outcome** | Receipt users receive timely WhatsApp contact for onboarding activation, one-off operational messages, and broadcast follow-ups, while operators can remove Twilio Conversations resources when they are no longer needed. |
| **Entry Point / Surface** | **Server-to-server:** Sleek Receipts `POST /api/external/send-post-save-message`, `POST /api/external/send-post-save-message-templates`, `POST /api/external/broadcast/:broadcast_message_id`, `POST /api/external/conversation/:conversationId/delete` (no app-specific auth middleware on the router in `index.js` — treat as trusted internal/integration surface unless an edge gateway applies auth). |
| **Short Description** | Integrations send plain WhatsApp body text via Twilio Messages; send Twilio Content activation templates after resetting/initialising Redis receipt-user and activation sessions; run broadcast campaigns keyed by `broadcast_message_id`, optionally retrying failed sends or limiting to test numbers, resolving recipients through Sleek Back receipt-user data; and delete a Twilio Conversations conversation by SID. Template and broadcast sends persist to MongoDB and use the templates Twilio subaccount; ad-hoc body sends use the main Twilio client and do not create `WhatsappConversation` rows in the reviewed path. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Sleek Back:** `CompanyGetter.getAllReceiptUsersOrFilterViaPhoneNumbers` (and phone lists) for broadcast audience. **Twilio:** Messages API (`sendStandardWhatsappMessage`, `sendTwilioWhatsappMessage`), Conversations API `conversations(conversationId).remove()`, separate env credentials for template account vs receipts account. **Redis:** `resetAndInitializeSession`, `initializeNumberVerificationSession` for activation template flow (`TWILIO_REDIS_KEYS`). **Related inventory:** `accounting/twilio-whatsapp/send-whatsapp-messages-to-clients.md` (shared `createConversationAndSendMessage` / template pipeline). |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `whatsappconversations` (Mongoose `WhatsappConversation`) — create/update for template sends and broadcast rows; ad-hoc `POST /send-post-save-message` does not write this collection in the reviewed code. **Redis** — session keys for activation/onboarding when templates are triggered with `messageType === "activation"`. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | How these `/api/external` routes are authenticated or restricted in production (VPC, API gateway, shared secret not visible on the router). Whether `createdBroadcastConversationAndSendMessage` passes `contentSid` correctly when `message` is plain text (implementation uses `message` as second arg to `sendTwilioWhatsappMessage` — confirm against Twilio Content API expectations). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Routes** — `src/routes/external-requests.js`:
  - `POST /send-post-save-message` → `conversationService.sendStandardWhatsappMessage(client, phoneNumber, message)` (`RECEIPTS_ACCOUNT_SID` / `messages.create` body to `whatsapp:{phone}`).
  - `POST /broadcast/:broadcast_message_id` → optional `getFailedBroadcastMessagesByMessageId`, `CompanyGetter.getAllReceiptUsersOrFilterViaPhoneNumbers`, `createdBroadcastConversationAndSendMessage` per unique number (500 ms delay), optional `test_flight` / `test_flight_phone_numbers`.
  - `POST /send-post-save-message-templates` → if `messageType === "activation"`, `TwilioWhatsappService.resetAndInitializeSession(phoneNumber)`, `initializeNumberVerificationSession(phoneNumber)`; then `createConversationAndSendMessage` with `TEMPLATE_TYPES.ACTIVATION` and `params.firstName` / `params.lastName`.
  - `POST /conversation/:conversationId/delete` → `client.conversations.conversations(conversationId).remove()` (errors logged, still returns JSON).
- **Conversations (plain send)** — `src/services/conversations.js`: `sendStandardWhatsappMessage` uses `validSender` (`RECEIPTS_ACCOUNT_VALID_SENDER`) and Twilio `messages.create`; also exports `findConversation`, `createConversation`, `initializeParticipants` for Conversations API usage elsewhere.
- **Templates & broadcast persistence** — `src/services/twilio-whatsapp-conversations.js`: `WhatsappConversation` create/update; `createConversationAndSendMessage` (`TWILIO_TEMPLATE_MESSAGE`, `sendTwilioWhatsappMessage` with `contentSid`); `createdBroadcastConversationAndSendMessage` (skip if already delivered; `broadcast_message_id`, `message_is_delivered`); `getFailedBroadcastMessagesByMessageId` (`status: "failed"`, `message_is_delivered: false`).
- **Activation session helpers** — `src/services/twilio-whatsapp.service.js`: `resetAndInitializeSession`, `initializeNumberVerificationSession` (Redis activation session), used from external-requests for activation template path; large inbound `receiveMessage` flow is separate but shares `createConversationAndSendMessage`.
- **Receipt user resolution** — `src/companies/get.js`: `getAllReceiptUsersOrFilterViaPhoneNumbers` → `SLEEK_BACK_API.getAllReceiptUsersOrFilterViaPhoneNumbers`.
- **Schema** — `src/schemas/whatsapp-conversation.js`: model `WhatsappConversation` including `broadcast_message_id`, `message_is_delivered`, `status`, `sid`, etc.
- **App mount** — `index.js`: `app.use("/api/external", ExternalRequestsRouter)`.
