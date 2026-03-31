# Cross-repo map: customer-mfe, sleek-back, sleek-website

Draft **inventory aid**: how **sleek-back**, **sleek-sign** (backend), **customer-mfe**, and **sleek-website** relate, where surfaces live, and first-pass **audit-hub Domain** hints. This is not a substitute for product-owner validation.

See also: [inventory-scope-and-domains.md](./inventory-scope-and-domains.md) (checklist + `sleek-back` `/v2` router hints).

## Roles of each repo


| Repo                   | Role                                                                                                 | Primary evidence                                                                                           |
| ---------------------- | ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **sleek-back**         | Shared Node/Express monolith API (legacy + `/v2/*`); MongoDB; many integrations                      | `app.js`, `app-router.js`, `controllers/`, `controllers-v2/`                                               |
| **sleek-sign** (backend) | Dedicated **Sleek Sign** API service (Express, Postgres, S3, SQS)                                     | `sleek-sign-backend/v1/app.js`, `routes/`, `routes-v2/`                                                    |
| **customer-mfe**       | Customer-facing Vue micro-frontends (portal, dashboard, onboarding, sleek-sign shell, etc.)          | `customer-main/`, `customer-common/`, `customer-dashboard/`, `sleek-sign/`, `customer-onboarding-vue3/`, … |
| **sleek-website**      | Staff **admin** site (Marko pages + React); opens customer sleek-sign in new tab with `origin=admin` | `pages/admin/**/*.marko`, `src/views/admin/`, `src/components/new-admin-side-menu.js`, `src/utils/api.js`  |


## Backend URLs (sleek-website → services)

From `sleek-website/src/utils/api.js` (and related helpers):


| Config / env                                         | Typical use                                                                                  |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `API_BASE_URL`                                       | Primary **sleek-back** REST base; many calls rewrite to `${base}/admin/...` for admin routes |
| `CUSTOMER_WEBSITE_URL`                               | Customer app host (deep links from admin, e.g. sleek-sign)                                   |
| `FILE_BASE_URL`                                      | File microservice                                                                            |
| `SUBSCRIPTION_API` / `PAYMENT_API`                   | Subscription / payment services (often separate ports in dev)                                |
| `DEADLINE_API_BASE_URL` (via `getAppCustomEnv`)      | Deadlines                                                                                    |
| `COMPANY_ROLES_API_BASE_URL` (via `getAppCustomEnv`) | Company roles service                                                                        |


**customer-mfe** generally targets **sleek-back** through per-package env (e.g. `VUE_APP_PLATFORM_API`, `VUE_APP_PLATFORM_APP_URL`).

## Authentication (inventory rule)

- **Sleek Auth** remains the canonical **Platform** authentication story in [authentication/](./authentication/).
- **Legacy** staff login still uses `sleek-website` → `sleek-back` paths such as `/users/login`, `/users/logout`, plus optional **Auth0** / **SSO** (`src/utils/api-utils.js`: `app-origin`, `Bearer` token, CMS-driven `auth0` / `sso` feature flags).
- **Do not** add duplicate master-sheet **Authentication** rows for those legacy flows; cite them here and under repo scan notes as **migration context**.

## sleek-website — admin information architecture

### Side menu entry points (subset)

Evidence: `src/components/new-admin-side-menu.js` (`href="/admin/..."`).


| Path                                                                                           | Menu context (short)       |
| ---------------------------------------------------------------------------------------------- | -------------------------- |
| `/admin/dashboard/`, `/admin/`                                                                 | Dashboard / home           |
| `/admin/companies/`                                                                            | Companies                  |
| `/admin/new-workflow/`, `/admin/sleek-workflow/`, `/admin/my-tasks/`                           | Workflows / tasks          |
| `/admin/print-documents/`, `/admin/files/`, `/admin/accounting/`, `/admin/mailroom/`           | Documents / accounting ops |
| `/admin/accounts/`, `/admin/business-account-statuses/`, `/admin/transactions/`, `/admin/rfi/` | Banking / RFI              |
| `/admin/requests/`                                                                             | Requests                   |
| `/admin/subscriptions/new/`, `/admin/coupons/`                                                 | Subscriptions / coupons    |


Additional **pages** exist beyond the side menu (fuller list): run `node scripts/pages.js --list` in `sleek-website` or see `pages/admin/**/*.html.marko`.

### Admin areas → first-pass Domain + API tendency

Grouped for the master sheet (confirm with POs).


| Admin area (examples)                                                                                                     | First-pass Domain                                     | Usually backed by                                                            |
| ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------------------- |
| Companies, company overview, company billing, corpsec, registers, secretary, EP                                           | **Corpsec** / **SBC**                                 | **sleek-back** (`/admin`, legacy controllers, `/v2/corpsec`, …)              |
| New workflow, Sleek workflow, my tasks, requests, templates, migration                                                    | **SBC** / ops (or **SDET** if treated as engine-only) | **sleek-back** workflows, Camunda-related `/v2/*`                            |
| Subscriptions, coupons, invoices, transactions, accounts, RFI, billing configuration, incomplete / paid-incomplete orders | **Bookkeeping & Accounting** / billing                | **sleek-back** + subscription/payment URLs                                   |
| Accounting (admin), mailroom, files, documents, print, recovery                                                           | **Bookkeeping** / **SBC**                             | **sleek-back** + **file** service                                            |
| Services, service configuration                                                                                           | **SBC**                                               | **sleek-back**                                                               |
| Customer support, dashboard (ops)                                                                                         | **SBC** / support                                     | **sleek-back**                                                               |
| KYC activity, CDD answers (under sleek-workflow)                                                                          | **Compliance**                                        | **sleek-back** + compliance integrations                                     |
| Access — groups, permissions; audit logs; user management                                                                 | **Platform** (authz / audit)                          | **sleek-back** admin + authz; may overlap [authorization/](./authorization/) |
| Auto-sign configuration                                                                                                   | **Sleeksign**                                         | **sleek-back** + Sleeksign; see [sleeksign/README.md](./sleeksign/README.md) |
| User management (admin users)                                                                                             | **Platform** / **SBC** (confirm)                      | **sleek-back**                                                               |


## customer-mfe — packages (customer surface)


| Package                                                 | Role (short)                                                               |
| ------------------------------------------------------- | -------------------------------------------------------------------------- |
| `customer-main`                                         | Main customer portal shell, modules, proxies to **sleek-back**             |
| `customer-common`                                       | Shared library, proxies (e.g. sleek-access-control, company-roles), stores |
| `customer-dashboard`                                    | Dashboard MFE                                                              |
| `customer-onboarding-vue3`                              | Onboarding (uses `/v2/config/platform/customer/`, etc.)                    |
| `sleek-sign`                                            | E-sign **Vue** MFE; proxies to **sleek-sign-backend** and **sleek-back** — [sleeksign/](./sleeksign/) |
| `customer-acquisition`, `customer-sba`, `customer-root` | Other entry / acquisition flows                                            |


Feature-level mapping: follow modules under `customer-main/src/modules/` and `**/proxies/back-end/**`; assign **Domain** by outcome (see checklist in [inventory-scope-and-domains.md](./inventory-scope-and-domains.md)).

## sleek-back — API map

Use the **`/v2/`** mount table in [inventory-scope-and-domains.md](./inventory-scope-and-domains.md). Legacy `controllers/**/*.js` routes (mounted at `/`) cover many admin and customer endpoints; **admin** variants are often under `controllers/admin/*` or rewritten via `api.js` to `/admin/...`.

## sleek-sign — backend API (Sleeksign domain)

Inventory: [sleeksign/README.md](./sleeksign/README.md). **`/v2/*`** (with `tenantIdGateway`): drafts, templates, contacts, free-user and OTP flows, admin void/mark-complete, reminders. **`/document/*`**: legacy signing and lifecycle. Other mounts in `sleek-sign-backend/v1/app.js`: user signatures, initials, uploads, webhooks, healthcheck.

## Shared Platform touchpoints across all three


| Concern                            | Where it shows up                                                                                                                                                                             |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CORS whitelist / CMS-driven config | **sleek-back** health + `cms-controller` cache webhook; **customer-mfe** / **sleek-website** rely on valid config — [sleek-cms-sdk-and-platform-config.md](./external-integrations/sleek-cms-sdk-and-platform-config.md) |
| Partner white-label                | **customer-mfe** `Origin` → **sleek-back** `req.partner` ([external-integrations/sleek-back-partner-origin-white-label.md](./external-integrations/sleek-back-partner-origin-white-label.md)) |
| Staff vs customer auth headers     | **sleek-website** `api-utils.js` (`app-origin`, Auth0 bearer); **customer-mfe** Auth0 + legacy token patterns                                                                                 |
| Rate limiting                      | **sleek-back** global limiter ([operations/sleek-back-monolith-health-and-rate-guard.md](./operations/sleek-back-monolith-health-and-rate-guard.md))                                          |


## Scan notes per repo


| Repo          | README                                                                           |
| ------------- | -------------------------------------------------------------------------------- |
| sleek-back    | [scans-pending/sleek-back/README.md](./scans-pending/sleek-back/README.md)       |
| customer-mfe  | [scans-pending/customer-mfe/README.md](./scans-pending/customer-mfe/README.md)   |
| sleek-website   | [scans-pending/sleek-website/README.md](./scans-pending/sleek-website/README.md)   |
| sleek-sign (API) | [scans-pending/sleek-sign-backend/README.md](./scans-pending/sleek-sign-backend/README.md) |


## Appendix: sleek-website `pages/admin` routes (draft list)

Generated from repo layout (`pages/admin/**/*.html.marko`). Use as a checklist when filing master-sheet rows; names are path hints, not final feature titles.


| Route                                     |
| ----------------------------------------- |
| `/admin/access/groups/`                   |
| `/admin/access/permissions/`              |
| `/admin/accounting/`                      |
| `/admin/accounts/`                        |
| `/admin/audit-logs/`                      |
| `/admin/auto-sign-configuration/`         |
| `/admin/billing-configuration/`           |
| `/admin/business-account-statuses/`       |
| `/admin/companies/`                       |
| `/admin/companies/edit/`                  |
| `/admin/companies/registers/`             |
| `/admin/company-billing/`                 |
| `/admin/company-overview/`                |
| `/admin/corpsec/allocation/`              |
| `/admin/corpsec/company-allocation/`      |
| `/admin/corpsec/my-tasks/`                |
| `/admin/corpsec/team-timeline/`           |
| `/admin/coupons/`                         |
| `/admin/customer-support/`                |
| `/admin/customer-support/company/`        |
| `/admin/customer-support/create-company/` |
| `/admin/dashboard/`                       |
| `/admin/documents/`                       |
| `/admin/ep/`                              |
| `/admin/ep/edit/`                         |
| `/admin/files/`                           |
| `/admin/incomplete-orders/`               |
| `/admin/` (home — `index.html.marko`)     |
| `/admin/invoices/reconcile/`              |
| `/admin/invoices/update-services/`        |
| `/admin/kyc-activity/`                    |
| `/admin/mailroom/`                        |
| `/admin/migration-form/`                  |
| `/admin/my-tasks/`                        |
| `/admin/new-coupons/`                     |
| `/admin/new-coupons/create-edit/`         |
| `/admin/new-workflow/`                    |
| `/admin/new-workflow/my-tasks/`           |
| `/admin/new-workflow/workflow-task/`      |
| `/admin/paid-incomplete-orders/`          |
| `/admin/print-documents/`                 |
| `/admin/recovery/`                        |
| `/admin/recovery/recovery-files/`         |
| `/admin/request-templates/`               |
| `/admin/requests/`                        |
| `/admin/requests/edit/`                   |
| `/admin/requests/new/`                    |
| `/admin/rfi/`                             |
| `/admin/rfi/detail/`                      |
| `/admin/secretary/`                       |
| `/admin/service-configuration/`           |
| `/admin/services/`                        |
| `/admin/services/edit/`                   |
| `/admin/services/new/`                    |
| `/admin/sleek-workflow/`                  |
| `/admin/sleek-workflow/cdd-answers/`      |
| `/admin/sleek-workflow/my-tasks/`         |
| `/admin/sleek-workflow/workflow-task/`    |
| `/admin/subscriptions/cancellation/`      |
| `/admin/subscriptions/new/`               |
| `/admin/subscriptions/new/details/`       |
| `/admin/subscriptions/paid/`              |
| `/admin/subscriptions/paid/edit/`         |
| `/admin/subscriptions/unpaid/`            |
| `/admin/transactions/`                    |
| `/admin/user-management/`                 |
| `/admin/workflow/`                        |


## Related

- [README.md](./README.md)
- [Sleek Feature Scope Audit Hub](../Sleek%20Feature%20Scope%20Audit%20Hub.md)

