# Activate WhatsApp receipt service

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Activate WhatsApp receipt service |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User |
| **Business Outcome** | The user’s WhatsApp number is linked to Sleek so they can capture receipts on WhatsApp after onboarding. |
| **Entry Point / Surface** | WhatsApp (Twilio Studio receipt flow) → user sends activation code message; webhook `POST /api/twilio/service-activation` |
| **Short Description** | When a user messages the Sleek WhatsApp line with an activation code (and no competing media/thumb shortcut), the service loads the inbound message from Twilio, strips the `whatsapp:` prefix from the sender, and calls Sleek-back to validate and apply the code. The Twilio response speaks the API result or a standard activation error message. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Twilio Conversations/Messages API (`retrieveMessageDetails`); Sleek-back `POST external-receipts/service-activation` (activation persisted server-side); downstream WhatsApp receipt submission flows after the number is linked |
| **Service / Repository** | sleek-receipts; sleek-back (external API) |
| **DB - Collections** | None in sleek-receipts for this handler; activation state is owned by Sleek-back |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether v2 `/api/twilio/v2/service-activation` intentionally routes to `setInitialStep` instead of activation (may be legacy or misconfiguration); confirm market-specific activation rules in Sleek-back only |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### HTTP surface (`src/routes/twilio.js`)

- `POST /service-activation` → `TwilioController.activateService` (app mount: `POST /api/twilio/service-activation` in `index.js`). Unlike other Twilio routes in this file, this handler is not wrapped in `twilioTokenAuth` (Twilio Studio posts the webhook body directly).

### Controller (`src/controllers/twilio.js`)

- **`activateService`** — Loads Twilio memory; if `media` is set or `CurrentInput` is a thumb emoji (`THUMB_EMOJIS`), responds with `redirect` to `task://initial-step` (receipt flow) instead of activation. Otherwise reads `memoryData.twilio["messaging.whatsapp"].MessageSid`, calls `conversationService.retrieveMessageDetails(client, messageId)` to obtain the inbound WhatsApp message, uses `message.body` as the activation code and strips `whatsapp:` from `message.from` for the phone number. On success, `say` uses `(await SLEEK_BACK_API.activateServiceViaPhoneAndCode(...)).data.message`. On error, `say` uses `ERRORS.ACTIVATION_ERROR.message` from `constants/errors.js`.

### Twilio Messages API (`src/services/conversations.js`)

- **`retrieveMessageDetails`** — `client.messages(messageSid).fetch()` (Twilio REST client initialized with `RECEIPTS_ACCOUNT_SID` / `RECEIPTS_ACCOUNT_AUTH_TOKEN` at top of controller).

### Sleek-back (`src/external-api/sleek-back.js`)

- **`activateServiceViaPhoneAndCode`** — `POST` to path `external-receipts/service-activation` with JSON `{ whatsappNumber, activationCode }` via shared `AXIOS_DEFAULTS.createDefaultAxiosObject`.

### Related

- Separate path `POST /api/twilio/v2/service-activation` in the same routes file maps to `TwilioV2Controller.setInitialStep`, not activation—worth confirming intent vs legacy Studio configuration (see Open Questions).
