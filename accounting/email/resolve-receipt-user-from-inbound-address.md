# Resolve receipt user from inbound email address

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Resolve receipt user from inbound email address |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (in-process callers such as `EmailForwarderService`; external or internal HTTP clients that call the lookup API) |
| **Business Outcome** | Callers can determine which receipt user and tenant own a given inbound `email_in_address`, so inbound receipt mail and automation route to the correct context instead of failing or mis-delivering. |
| **Entry Point / Surface** | Sleek Receipt Gateway HTTP API: `GET /email` with required query `email_in_address` (documented in `src/docs/openapi.yaml`). Programmatic use inside the gateway: `EmailService.findEmailByEmailInAddress`. Not an end-user app screen. |
| **Short Description** | Queries the gateway `Email` store for a single document matching `email_in_address` (stored lowercased, unique), merging an optional caller-supplied filter (for example `status: ENABLED`). Returns fields including `receipt_user_id`, `tenant`, and `status` used to choose downstream behaviour (for example forwarding to the correct market inbox). |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | **Upstream:** Rows must exist and stay current—see [Sync receipt inbox from Sleek Back](sync-receipt-inbox-from-sleek-back.md) (`syncReceiptUsers`, cron delta, `POST /email/sync`). **Downstream:** `EmailForwarderService.sendEmailToReceipt` calls this with `status: EmailStatus.ENABLED` before forwarding; missing rows trigger failure handling and invalid-address mail paths. |
| **Service / Repository** | sleek-receipt-gateway |
| **DB - Collections** | `emails` (Mongoose model `Email`; connection `SLEEK_RECEIPT_GATEWAY`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `GET /email` is restricted by API gateway, network policy, or auth is not visible on `EmailController` (no route-level guards in the reviewed files). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/modules/email/email.controller.ts`**: `GET /` on `@Controller('email')` — `findEmailByEmailInAddress(@Query('email_in_address') emailInAddress)` delegates to `EmailService.findEmailByEmailInAddress(emailInAddress)` (no `@ApiOperation` on this handler; other routes document sync operations).
- **`src/modules/email/email.service.ts`**: `findEmailByEmailInAddress(emailInAddress, filter?)` builds `{ ...filter, email_in_address: emailInAddress }` and runs `this.emailModel.findOne(...)`; logs with `maskEmail` for privacy.
- **`src/modules/email/models/email.schema.ts`**: `email_in_address` required, unique index, lowercased on set; `receipt_user_id`, `tenant` (comment lists SG, HK, UK, AU), `status` (`EmailStatus`).
- **`src/modules/email/email-forwarder/email-forwarder.service.ts`**: `sendEmailToReceipt` calls `findEmailByEmailInAddress(emailMessage.emailInAddress, { status: EmailStatus.ENABLED })`; on empty result, marks log failed and sends invalid-user email; on success uses `email.tenant` to resolve `RECEIPT_EMAILS[tenant]` for forwarding.
- **`src/docs/openapi.yaml`**: Path `/email` GET, parameter `email_in_address` required, `operationId: EmailController_findEmailByEmailInAddress`.
