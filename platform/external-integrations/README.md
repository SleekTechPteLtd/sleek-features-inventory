# External integrations (category)

**Third-party and asynchronous touchpoints** that are not “normal” user login in the browser: Auth0 custom database scripts, signed webhooks, **Sleek CMS** (SDK, webhooks, Kafka-driven sync), etc. Also **channel / tenant bridges** such as white-label partner resolution from HTTP `Origin` on the legacy monolith.

Authentication and IAM **product** features stay in [../authentication/](../authentication/) and [../authorization/](../authorization/); this folder is for **bridges** to other systems (or explicit partner-channel wiring).

## Capability documents

| Document | Short description |
|----------|-------------------|
| [internal-auth0-bridge.md](./internal-auth0-bridge.md) | Internal API for Auth0 custom DB / claims |
| [auth-event-webhooks.md](./auth-event-webhooks.md) | Inbound signed webhooks (e.g. email-related auth events) |
| [sleek-back-partner-origin-white-label.md](./sleek-back-partner-origin-white-label.md) | `req.partner` from `Origin` on `sleek-back` |
| [sleek-cms-sdk-and-platform-config.md](./sleek-cms-sdk-and-platform-config.md) | `@sleek-sdk/sleek-cms`, config API, cache + CORS sync |
| [customer-mfe-localization-english-chinese.md](./customer-mfe-localization-english-chinese.md) | CMS-gated EN/ZH localization toggle in customer portal |
