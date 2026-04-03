# List accounting companies for internal integration

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | List accounting companies for internal integration |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Internal tools (e.g. CIT) can discover which companies are live under allowed statuses and carry at least one active accounting subscription line that matches the configured accounting-service catalogue, so cross-system workflows stay scoped to the right customer base. |
| **Entry Point / Surface** | Internal HTTP API on sleek-back: `GET /accounting-companies`. Guard: `generalAuthMiddlewareV2("SLEEK_CIT_API_TOKEN")` — caller must send `Authorization` matching the `SLEEK_CIT_API_TOKEN` environment variable (token auth for service-to-service use; not a browser or end-user session). |
| **Short Description** | Resolves the set of accounting service internal names via subscription helpers and app-feature-driven tags, loads allowed company statuses from admin constants, then queries MongoDB for companies whose embedded subscription lines include an active accounting service from that set. Returns JSON `{ companies }` with `uen`, `_id`, `name`, `status`, and `subscriptions`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **App features**: `admin_constants.general.ALLOWED_STATUSES`, accounting services derived via `getAccountingSubscriptionByTags` (which may read **Sleek Billings** `getServices` when accounting tags are enabled, otherwise static props from app features). **Tenant**: `ACTIVE` from `tenant.general.MAPS_CONSTANTS.SUBSCRIPTION_STATUSES`. **Related**: `getValidAccountingSubscriptionListByCompanyId` in the same subscription module is used elsewhere (e.g. receipts) to validate accounting subscriptions per company via microservice or Sleek Billings — not invoked by this list endpoint. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies` (read: `status`, `subscriptions`, plus projected `uen`, `name`, `_id`). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | “CIT” is only named in a code comment; exact consuming systems beyond token name are not enumerated in these files. Whether production `ALLOWED_STATUSES` and tag-driven accounting service lists differ by market is configuration-dependent. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/company-controller.js`

- **`GET /accounting-companies`** — `generalAuthMiddlewareV2("SLEEK_CIT_API_TOKEN")`; comment references fetching accounting companies for CIT.
- Handler flow: `appFeatureUtil.getAppFeatureList()` → `getAppFeaturePropByNameAndCategory(..., 'admin_constants', 'general')` → `ALLOWED_STATUSES` value array.
- **`subscriptionService.getAccountingSubscriptionByTags([TAGS.ENABLE_ACCOUNTING_PAGE_IN_CUSTOMER_APP])`** — yields `ACCOUNTING_SERVICES_VALUES` (service internal names) used in the query filter.
- **`Company.find`** — `status` ∈ allowed statuses; `subscriptions.status` === `ACTIVE`; `subscriptions.service` ∈ accounting service list; `.select("uen _id name status subscriptions")`.
- Response: `res.json({ companies })`.

### `modules/sleek-subscription/services/subscription.service.js`

- **`getAccountingSubscriptionByTags(tags)`** — When accounting tags feature flag is off, returns accounting services from app-feature props; when on, loads services from `sleekBillingsService.getServices(CLIENT_TYPE.MAIN)` and filters by `SUBSCRIPTION_SERVICE_TYPE.ACCOUNTING` and tag overlap; returns internal names for matching subscriptions.
- **`getValidAccountingSubscriptionListByCompanyId(companyId)`** — Exported helper: Sleek Billings path with `SUBSCRIPTION_SERVICE_TYPE.ACCOUNTING`, or sleek-subscription HTTP API with `serviceType=accounting`, filters out `inactive` legacy rows, maps via `mapSubscription` / `mapSubscriptionFromSleekBillings`. **Not called** by `GET /accounting-companies`; documents shared “active accounting subscription” semantics in the same module.

### `tests/controllers/company-controller/accounting-companies.js`

- **`GET /accounting-companies`** — Expects `200` and populated `companies` when `Authorization` matches `process.env.SLEEK_CIT_API_TOKEN`; `422` without auth header; `403` when token does not match.
