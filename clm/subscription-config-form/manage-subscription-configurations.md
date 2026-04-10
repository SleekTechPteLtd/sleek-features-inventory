# Manage Subscription Configurations

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Subscription Configurations |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (CLM operator / Billing Admin) |
| **Business Outcome** | Enables operators to centrally define and maintain the catalogue of purchasable and sellable subscription products — capturing pricing, billing terms, Xero accounting mappings, revenue nature, and service deliverable links — so all downstream billing and delivery flows have accurate, up-to-date service definitions. |
| **Entry Point / Surface** | Sleek Billings Admin > Subscription Config (`/subscription-config`, `/subscription-config/create`, `/subscription-config/edit/:id`) |
| **Short Description** | Operators browse, filter, create, edit, and delete subscription service configurations. Each record captures service name, code, service type, pricing (purchase/sell), billing cycle, duration, recurrence, display contexts, add-ons, Xero account and tax-rate mappings, revenue nature, tier, grouping criteria, and tags. A sync workflow pulls pending changes from a remote server for selective review and application; a change log provides an audit trail. In non-SIT/development environments the form is read-only — edits require a Billing Support Slack request. |
| **Variants / Markets** | SG, HK, AU, UK (revenue nature options are market-specific; HK platform additionally shows a Chinese translation field for the service name, detected from `billingConfig.platform` in localStorage) |
| **Dependencies / Related Flows** | Xero (chart-of-accounts and tax rates via `/xero/accounts`, `/xero/tax-rates` filtered by `clientType`); Sleek Service Delivery API (`GET /deliverable-templates/deliverable-templates-list` — templates linked to subscription code); Delivery Config screen (`/delivery-config`); Remote server sync (`GET /subscription-config/changes`, `PUT /subscription-config/changes/sync`); Customer Subscriptions (consumes configs); Invoice and billing flows |
| **Service / Repository** | sleek-billings-frontend, sleek-billings-backend (inferred) |
| **DB - Collections** | Unknown (frontend only; backend likely owns a `subscriptionConfig` or `subscription-config` collection) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which backend repo owns the `/subscription-config` API? What is the "remote server" that sync pulls from (ERPNext, another Sleek environment)? Are create/delete permanently production-disabled or only guarded by the environment flag? `clientType` values `main` vs `manage_service` — what does this distinction represent in the business? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/pages/SubscriptionConfig/SubscriptionConfigList.jsx` — list view with filters (billing cycle, service type, status, recurring, display-in, add-ons), search by code/name/price, client-type switcher (main / manage_service / all), sync-changes dialog (grouped by create/update/delete with selective apply), sync-logs dialog
- `src/pages/SubscriptionConfig/SubscriptionConfigForm.jsx` — create/edit/delete form organised into General, Billing, and Delivery sections; read-only guard based on `localStorage.environment`

### API calls (`src/services/api.js`)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/subscription-config` | Fetch all configs |
| GET | `/subscription-config/:id` | Fetch single config |
| POST | `/subscription-config` | Create config |
| PUT | `/subscription-config` | Update config |
| DELETE | `/subscription-config/:id` | Delete config |
| GET | `/subscription-config/changes?clientType=` | Preview pending sync changes from remote server |
| PUT | `/subscription-config/changes/sync?clientType=` | Apply selected sync changes |
| GET | `/subscription-config/sync/logs` | Retrieve sync audit log |
| GET | `/xero/accounts` (param: `clientType`) | Xero chart-of-accounts for account-code mapping |
| GET | `/xero/tax-rates` (param: `clientType`) | Xero tax rates for tax-type mapping |

### External service calls
- `sleekServiceDeliveryApi.getDeliverableTemplatesList()` → `GET /deliverable-templates/deliverable-templates-list` — fetches all deliverable templates, then filters client-side by subscription `code`; cross-links to the Delivery Config feature

### Key form fields
- **General**: `serviceName`, `internalName` (auto-derived), `code`, `translatedNames.zh` (HK only)
- **Billing — Purchase**: `isPurchased`, `purchasePrice`, `purchaseAccountCode` (Xero), `purchaseTaxType` (Xero), `purchaseDescription`
- **Billing — Sell**: `isSold`, `price`, `accountCode` (Xero), `taxType` (Xero), `description`
- **Billing — Classification**: `type` (corporate_secretary / accounting / immigration / mailroom / business_account / …), `display` (admin / customer / paymentRequest), `tier`, `metaNumber`, `status` (active / inactive), `duration` (months), `recurring`, `billingCycle` (calendar_year / financial_year / monthly), `subscriptionGroupingCriteria`, `subscriptionGroupingNoOfInstances`, `revenueNature` (market-specific list), `tags`, `subscriptionAddons`
- **Delivery**: read-only linked deliverable templates filtered by subscription code; links out to `/delivery-config/edit/:id`
- **Other**: `isTest` (marks record for testing purposes), `clientType` (main / manage_service), `externalId`

### Code auto-derivation rules
- Code prefix `AC-` → type `accounting`, `CO-` → `corporate_secretary`, `PN-` → `business_account`
- Code containing `-RE-` → `recurring = true`; `-OT-` → `recurring = false`
- Recurring → default display includes `customer`; one-time → excludes `customer`
- Selecting a Xero account code auto-populates its associated tax type

### Access control
- Form is fully read-only when `localStorage.environment` is not `sit` or `development`; a banner instructs users to submit edits via Billing Support Slack
- "Create New Configuration" button is hidden in non-SIT/development environments
- Sync and audit-log actions appear available in all environments
