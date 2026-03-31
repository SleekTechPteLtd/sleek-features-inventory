# Auth event webhooks (inbound)

## Master sheet (draft)


| Column                           | Value                                                                                                     |
| -------------------------------- | --------------------------------------------------------------------------------------------------------- |
| **Domain**                       | Platform                                                                                                  |
| **Feature Name**                 | Verify and process signed authentication webhooks                                                         |
| **Canonical Owner**              | TBD                                                                                                       |
| **Primary User / Actor**         | External webhook emitter (e.g. email/auth vendor)                                                         |
| **Business Outcome**             | React to auth-related events (e.g. delivery notifications) without polling                                |
| **Entry Point / Surface**        | `POST /webhook/email` with signature headers                                                              |
| **Short Description**            | Validates `webhook-id`, `webhook-signature`, `webhook-timestamp` against raw body, then processes payload |
| **Variants / Markets**           | Additional webhook topics if extended beyond `email`                                                      |
| **Dependencies / Related Flows** | User/email lifecycle                                                                                      |
| **Service / Repository**         | `sleek-auth` `src/webhook/controllers/webhook.controller.ts`, `WebhookService`                            |
| **DB - Collections**             | TBD                                                                                                       |
| **Evidence Source**              | Codebase                                                                                                  |
| **Criticality**                  | Medium                                                                                                    |
| **Usage Confidence**             | Low–Medium (confirm production usage with ops)                                                            |
| **Disposition**                  | Must Keep                                                                                                 |
| **Open Questions**               | Which vendors emit to this endpoint in each environment                                                   |
| **Reviewer**                     |                                                                                                           |
| **Review Status**                | Draft                                                                                                     |


## Evidence

### sleek-auth

- `src/webhook/controllers/webhook.controller.ts`
- `src/webhook/services/webhook.service.ts`

### sleek-auth-ui

- N/A.

### sdk-auth-nest

- N/A.

