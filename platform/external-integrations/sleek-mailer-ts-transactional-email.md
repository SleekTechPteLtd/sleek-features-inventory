# Sleek Mailer (`sleek-mailer-ts`) — transactional email service

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Central transactional email delivery (templates, Kafka consumer, multi-provider) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Backend services publishing to Kafka; operators (optional Mailer UI); CMS for template updates |
| **Business Outcome** | Reliable outbound email for workflows (incorporation, documents, notifications) with templating and provider abstraction |
| **Entry Point / Surface** | Kafka topic consumer (`send-email` by default); HTTP `/api/health`; CMS webhook to refresh cache; optional Nuxt Mailer UI when `SLEEK_MAILER_UI` is enabled |
| **Short Description** | **sleek-mailer-ts** is a Node/TypeScript service that consumes send-email jobs from **Kafka**, renders **Pug** templates (and CMS-backed templates via `@sleek-sdk/sleek-cms`), and sends mail through **SendGrid**, **AWS SES**, or **local** engines. It exposes health with DB/streamer/mailer status, integrates **MongoDB** and **Redis**, and accepts **CMS webhooks** to refresh template cache. |
| **Variants / Markets** | Per-tenant BCC notification groups by `country_code`; `MAIL_ENGINE` (aws, sendgrid, local); template disable / mock flags |
| **Dependencies / Related Flows** | [sleek-cms-sdk-and-platform-config.md](./sleek-cms-sdk-and-platform-config.md) (CMS content); producers on shared Kafka topic (often monolith or other services) |
| **Service / Repository** | `sleek-mailer-ts` (Bitbucket `sleek-corp/sleek-mailer-ts`) |
| **DB - Collections** | MongoDB (`sleek_mailer` default per README env); Redis |
| **Evidence Source** | Codebase |
| **Criticality** | High |
| **Usage Confidence** | High (dedicated service + env docs) |
| **Disposition** | Must Keep |
| **Open Questions** | Which services are the primary Kafka producers per environment; ownership of Mailer UI vs ops-only |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-mailer-ts

- `package.json` — `@sendgrid/mail`, `aws-sdk`, `kafkajs`, `@sleek-sdk/sleek-cms`, `mongoose`, `redis`, `nodemailer`, `email-templates`, `pug`.
- `README.md` — env vars: `MAIL_ENGINE`, `KAFKA_*`, `CMS_BASE_URL`, `CMS_API_TOKEN`, `DB_*`, `SLEEK_MAILER_UI`, SendGrid/AWS keys.
- `src/streamer/streamer.loader.ts` / `src/streamer/handlers/send-email/send-email.ts` — Kafka-driven handler calling `MailerService().sendEmail`.
- `src/modules/email/services/mailer/mailer.service.ts` — template compilation via `TemplateService`, provider selection (AWS / SendGrid / local), optional DB persistence.
- `src/modules/health/routes/health.route.ts` — `GET /api/health` (database, streamer, mailer engine, UI config).
- `src/modules/webhook/controllers/cms/cms.controller.ts` — CMS webhook `updates` → `CMSService.refreshCache()`.
- `src/server.ts` — optional static UI from `ui/dist` when Mailer UI enabled.
- `src/modules/email/templates/**` — workflow-oriented Pug templates (e.g. `workflow_*`).

## Related

- [sleek-cms-sdk-and-platform-config.md](./sleek-cms-sdk-and-platform-config.md)
- [../operations/README.md](../operations/README.md) (health-style probes at service level)
