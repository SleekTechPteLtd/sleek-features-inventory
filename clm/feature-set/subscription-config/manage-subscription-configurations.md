# Manage Subscription Configurations

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Subscription Configurations |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables operators to centrally define and maintain the catalogue of purchasable and sellable services — capturing pricing, billing terms, Xero accounting mappings, and add-ons — so all downstream billing flows and service delivery tracking have accurate, up-to-date service definitions to work with. |
| **Entry Point / Surface** | Sleek Billings Admin > Subscription Config (`/subscription-config`, `/subscription-config/create`, `/subscription-config/edit/:id`) |
| **Short Description** | Operators browse, filter, create, edit, and delete subscription service configurations. Each record captures service name, code, service type, pricing (purchase/sell), billing cycle, duration, recurrence, display context, add-ons, Xero account and tax-rate mappings, revenue nature, and grouping criteria. A separate sync workflow pulls pending changes from a remote server for selective review and application, with a change log for audit. In non-SIT/development environments the form is read-only; edits require a Billing Support Slack request. |
| **Variants / Markets** | SG, HK, AU (HK platform shows Chinese translation field for service name; AU-specific priority labels seen in service-delivery-api subscription entity; platform detected from `billingConfig` in localStorage) |
| **Dependencies / Related Flows** | Xero (accounts and tax rates via `/xero/accounts`, `/xero/tax-rates`); sleek-service-delivery-api (subscribes to subscription config via MongoDB `customersubscriptions` → `services` aggregation lookup; syncs billing cycle, grouping criteria, service code/name into Supabase `subscriptions` table); Delivery Config screen (`/delivery-config`; deliverable templates linked to subscription code via `sleekServiceDeliveryApi.getDeliverableTemplatesList()`); Remote server sync (`/subscription-config/changes`, `/subscription-config/changes/sync`); Invoice and billing flows; Customer Subscriptions (consumes configs) |
| **Service / Repository** | sleek-billings-frontend (UI), sleek-billings-backend (inferred — owns `/subscription-config` API), sleek-service-delivery-api (downstream consumer — syncs subscription data including billingCycle, subscriptionGroupingCriteria from MongoDB `services` collection) |
| **DB - Collections** | MongoDB: `subscriptionconfigs` (inferred — backend collection for subscription config records; `services` collection stores linked service definition including `billingCycle`, `subscriptionGroupingCriteria`, `code`, `name` — confirmed by `sleek-billings.service.ts` aggregation); Supabase (PostgreSQL): `subscriptions` table (sleek-service-delivery-api — syncs billing metadata downstream) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which backend repo owns the `/subscription-config` API? (Not sleek-service-delivery-api — likely a separate billings backend.) What is the "remote server" that sync pulls from — another Sleek environment (e.g. SIT → prod) or a third-party source? Are create/delete permanently production-disabled or only guarded by environment flag? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/pages/SubscriptionConfig/SubscriptionConfigList.jsx` (sleek-billings-frontend) — list view with filters (billing cycle, service type, status, recurring, display-in, add-ons), search by code/name/price, client-type switcher (main / manage_service / all), sync-changes dialog with per-change selection, sync-logs dialog
- `src/pages/SubscriptionConfig/SubscriptionConfigForm.jsx` (sleek-billings-frontend) — create/edit form organised into General, Billing, and Delivery sections; read-only guard based on `localStorage.environment`
- `src/subscriptions/services/subscriptions.service.ts` (sleek-service-delivery-api) — `syncSubscription()` upserts into Supabase `subscriptions` table using data fetched from MongoDB; fields synced include `billingCycle`, `subscriptionGroupingCriteria`, `serviceDeliveryStatus`, `subscriptionRenewalStatus`
- `src/sleek-billings/services/sleek-billings.service.ts` (sleek-service-delivery-api) — `findCustomerSubscription()` runs MongoDB aggregation joining `customersubscriptions` → `services` → `invoices`; exposes `service.billingCycle`, `service.subscriptionGroupingCriteria`, `service.code`, `service.name`

### API calls (`src/services/api.js`, sleek-billings-frontend)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/subscription-config` | Fetch all configs |
| GET | `/subscription-config/:id` | Fetch single config |
| POST | `/subscription-config` | Create config (SIT/dev only) |
| PUT | `/subscription-config` | Update config (SIT/dev only) |
| DELETE | `/subscription-config/:id` | Delete config (SIT/dev only) |
| GET | `/subscription-config/changes?clientType=` | Preview pending sync changes from remote server |
| PUT | `/subscription-config/changes/sync?clientType=` | Apply selected sync changes |
| GET | `/subscription-config/sync/logs` | Retrieve sync audit logs |
| GET | `/xero/accounts` (header: `client-type`) | Xero chart-of-accounts for account code mapping |
| GET | `/xero/tax-rates` (header: `client-type`) | Xero tax rates for tax-type mapping |

### External service calls
- `sleekServiceDeliveryApi.getDeliverableTemplatesList()` — reads deliverable templates filtered by subscription `code`; cross-links to Delivery Config feature
- sleek-service-delivery-api calls MongoDB `customersubscriptions` / `services` collections (via `SleekBillingsService`) to sync subscription configs downstream into Supabase

### Key form fields
- **General**: serviceName, internalName, code, translatedNames.zh (HK only)
- **Billing**: type (corporate_secretary / accounting / immigration / mailroom / business_account), display (admin / customer / paymentRequest), tier, metaNumber, status (active / inactive), duration, recurring, billingCycle (calendar_year / financial_year / monthly), subscriptionGroupingCriteria, subscriptionGroupingNoOfInstances, revenueNature, tags, subscriptionAddons
- **Billing — Purchase**: isPurchased, purchasePrice, purchaseAccountCode (Xero), purchaseTaxType (Xero), purchaseDescription
- **Billing — Sell**: isSold, price, accountCode (Xero), taxType (Xero), description
- **Delivery**: read-only linked deliverable templates (navigates to `/delivery-config/edit/:id`)

### Access control
- Form is fully read-only when `localStorage.environment` is not `sit` or `development`
- "Create New Configuration" button hidden in non-SIT/development environments
- Sync and log actions available in all environments

### Downstream consumption (sleek-service-delivery-api)
- `Subscription` entity (`src/subscriptions/entities/subscription.entity.ts`) stores: `billingCycle`, `subscriptionGroupingCriteria`, `serviceDeliveryStatus`, `subscriptionRenewalStatus` — all sourced from MongoDB billing data
- `SubscriptionGroupingCriteria` determines FY grouping: when `same_fye` is in the service's groupingCriteria array, subscriptions are grouped into a `SubscriptionFyGroup`
- Priority labels are market-specific: SG (`AGM_DUE_SOON`, `SLEEK_ND`), HK (`PTR_RECEIVED`, `COURT_SUMMONS_RECEIVED`), AU (`ATO_DUE_SOON`, `BAS_DUE_SOON`, `COMPLIANCE_ACTION_REQUIRED`)
