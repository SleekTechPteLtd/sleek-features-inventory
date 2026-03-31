# Platform domain — feature inventory (draft)

Aligned with [Sleek Feature Scope Audit Hub](../Sleek%20Feature%20Scope%20Audit%20Hub.md). Docs are grouped by **larger product categories** (authentication vs authorization vs integrations vs **Sleeksign**, etc.), not by git repo. Each markdown file is still a draft **master-sheet row** plus **Evidence** that names the real code locations (`sleek-auth`, `sleek-sign-backend`, `customer-mfe`, …).

**Scope:** Most rows use spreadsheet **Domain** `Platform`. **Sleeksign** capabilities live under [sleeksign/](./sleeksign/) and use **Domain** `Sleeksign` in each file. For Platform vs Corpsec, Bookkeeping, etc.—and a **sleek-back router → domain** cheat sheet—see [inventory-scope-and-domains.md](./inventory-scope-and-domains.md).

**Repos map:** [cross-repo-sleek-surfaces-map.md](./cross-repo-sleek-surfaces-map.md) maps **customer-mfe**, **sleek-back**, **sleek-sign** (e-sign API), and **sleek-website** (admin) to surfaces, backends, and first-pass spreadsheet domains.

## Categories


| Category                  | What belongs here                                                                                                                                                      | Index                                                                |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| **Authentication**        | Identity, credentials, sessions, MFA, registration, password/email flows, tokens (user refresh + M2M), OAuth clients, captcha/T&C gates, **consuming JWT/M2M in Nest** | [authentication/README.md](./authentication/README.md)               |
| **Authorization**         | Policies, roles, permission catalog, user/org assignments, **local permission checks in Nest** (AuthZ SDK)                                                             | [authorization/README.md](./authorization/README.md)                 |
| **External integrations** | Auth0 custom DB bridge, inbound webhooks, **Sleek CMS** (SDK + config pipeline), **Sleek Mailer** (transactional email service), **Sleek Files Service** (storage/access APIs)                                                                                        | [external-integrations/README.md](./external-integrations/README.md) |
| **Operations**            | Health, aggregated stats, legacy monolith probes                                                                                                                       | [operations/README.md](./operations/README.md)                       |
| **Sleeksign**             | E-sign API, document lifecycle, templates, MFE shell (**Domain** `Sleeksign`, not `Platform`)                                                                          | [sleeksign/README.md](./sleeksign/README.md)                         |
| **Scans pending**         | Notes for **sleek-back**, **customer-mfe**, **sleek-website** scans (non-auth domains; see below)                                                                      | [scans-pending/](./scans-pending/)                                   |


## Sleek Auth vs legacy customer auth

**Authentication** rows in this folder describe **Sleek Auth** only. **sleek-back**, **customer-mfe**, and **sleek-website** (admin) still use legacy login / Auth0 / password flows against the monolith in places; treat those as **technical debt / migration context**, not duplicate Platform authentication features in the master sheet.

## Why not “one folder per repo”?

Repos are cited inside each file’s **Evidence** section. Top-level folders answer: *“Is this about proving identity, granting access, talking to a third party, or running the platform?”* For **sleek-back**, **customer-mfe**, and **sleek-website**, add capabilities under the category that matches the **outcome** while **avoiding auth overlap** with Sleek Auth (see [authentication/README.md](./authentication/README.md#scope-no-duplicate-auth-rows)).

## Conventions

- **Domain** column: `Platform` for [authentication/](./authentication/), [authorization/](./authorization/), [external-integrations/](./external-integrations/), [operations/](./operations/). Use `Sleeksign` for [sleeksign/](./sleeksign/). Other domains (Corpsec, Bookkeeping, …) should not be filed here except as noted in [inventory-scope-and-domains.md](./inventory-scope-and-domains.md).
- **Review Status**: `Draft` until product owners validate.
- Add new capabilities under the **category that matches the user story**, not necessarily the repo where most lines of code live.

