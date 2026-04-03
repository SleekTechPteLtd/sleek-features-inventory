# Recover WhatsApp Studio delivery failures

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Recover WhatsApp Studio delivery failures |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | When Twilio Studio cannot return the expected on-actions response or the upload path fails with a server error, the user still receives the intended prompt text or a clear failure notice on WhatsApp so the receipt flow does not go silent. |
| **Entry Point / Surface** | WhatsApp (Sleek receipts via Twilio Studio) — backend webhooks `POST /v2/autopilot/on-actions-fetch` and `POST /v2/error/webhook` (no in-app navigation). |
| **Short Description** | If Studio’s on-actions-fetch reports a non-success HTTP status for the `initial-step` task, the service extracts the `say` text that would have been returned and sends it via the Twilio Messaging API. If the Studio error webhook reports an ERROR with HTTP 502 on the upload path, it sends a fixed failure message the same way. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Twilio Studio / Autopilot (`initial-step` task), Twilio Messaging API (`messages.create`), upstream `setInitialStep` receipt dialogue; related to broader WhatsApp receipt submission and `twilio-v2-fillin` submission handling. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | None (these handlers only parse webhook bodies and call Twilio’s REST API; no MongoDB access in the recovery paths). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `ActionsHttpResponse` is always the string `"200"` for success in all Studio versions; whether other HTTP error codes besides 502 should trigger the upload-failure message. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/controllers/twilio-v2.js`**
  - **`retryInitialStep`**: Logs `onActionsFetch` webhook body. When `ActionsHttpResponse !== "200"` and `CurrentTask === 'initial-step'`, parses `Memory` JSON for `twilio.messaging.whatsapp.To` / `From`, wraps `res.send` to find the first `say` action in the payload, and if present with valid addresses calls `client.messages.create({ from, to, body: sayActionObj.say })` (Twilio SDK initialized with `RECEIPTS_ACCOUNT_SID` / `RECEIPTS_ACCOUNT_AUTH_TOKEN`). Then `next()` so `setInitialStep` can still run.
  - **`onErrorMessage`**: Logs error webhook body. When `Level === "ERROR"`, parses `Payload` JSON for `webhook.request.parameters.To` / `From` and `more_info.httpResponse`. If `httpResponse === '502'`, sends a fixed body: upload failed due to server issues, retry sending the document.
- **`src/routes/twilio.js`**: `POST /v2/autopilot/on-actions-fetch` chains `retryInitialStep` → `TwilioService.getCompaniesMiddleware` → `setInitialStep`; `POST /v2/error/webhook` → `onErrorMessage`.
