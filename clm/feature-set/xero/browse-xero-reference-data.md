# Browse Xero Reference Data

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Browse Xero Reference Data |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User, Admin |
| **Business Outcome** | Enables users to look up Xero-managed tax rates, chart of accounts, and billable service items so they can correctly configure billing and invoicing rules in the platform. |
| **Entry Point / Surface** | sleek-billings-backend API — `GET /xero/tax-rates`, `GET /xero/accounts`, `GET /xero/items` |
| **Short Description** | Fetches live reference data (tax rates, account codes, billable items/services) directly from a connected Xero organisation. Results are used downstream when configuring subscription line items, invoice defaults, and tax mapping rules. Tax rates are cached for 24 hours to reduce Xero API quota consumption. |
| **Variants / Markets** | SG, HK (multi-tenant via `client-type` header mapping to separate Xero tenants; exact market list Unknown) |
| **Dependencies / Related Flows** | Xero OAuth token management (`XeroSettingRepository`), Xero Settings update (`PUT /xero/settings`), Subscription / invoice configuration flows that consume account codes and tax types, `getExternalServiceList` (wraps `getItems` to expose billable services) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `xero_settings` (stores encrypted Xero OAuth credentials and active-token flags per `client-type`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which exact `ClientType` values map to which markets (SG/HK/other)? Is there a UI surface that calls these endpoints, or are they consumed by other backend services only? Cache invalidation strategy for accounts/items (only tax rates are cached currently)? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `xero/xero.controller.ts`

| Route | Guard | Service method | Notes |
|---|---|---|---|
| `GET /xero/tax-rates` | `@Auth()` | `xeroService.getTaxRates(clientType)` | Lazy init — skips `xeroService.init()` on cache hit |
| `GET /xero/accounts` | `@Auth()` | `xeroService.getAccounts()` | Returns `{code, name, taxType}` per account |
| `GET /xero/items` | `@Auth()` | `xeroService.getItems()` | Returns raw Xero `Item[]` |

`client-type` request header selects which Xero tenant to connect to (`ClientType.main` or backup).

### Service — `xero/services/xero.service.ts`

- **`getTaxRates(clientType?)`** (line 874): calls `xeroClient.accountingApi.getTaxRates(tenantId)`, maps to `{name, taxType, effectiveRate}`, caches result under key `xero_tax_rates_${clientType}` for **24 hours** via `@nestjs/cache-manager`.
- **`getAccounts()`** (line 925): calls `xeroClient.accountingApi.getAccounts(tenantId)`, maps to `{code, name, taxType}`.
- **`getItems()`** (line 286): calls `xeroClient.accountingApi.getItems(tenantId)`, returns full item list.
- **`getExternalServiceList()`** (line 1041): wraps `getItems()`, maps to `{id, code, name, description, price, taxType, accountCode}` — billing-friendly projection used by subscription/invoice configuration.
- **`clearTaxRatesCache()`** (line 919): cache invalidation helper for tax rates.
- Token selection: `XeroSettingRepository.findById(defaultTokenPersistKey)` determines active vs backup OAuth credentials; credentials are AES-encrypted at rest.

### Schema — `xero/models/xero-setting.schema.ts`

Collection `xero_settings`: fields `_id` (token key string), `value` (encrypted token set), `clientId`, `clientSecret` (both encrypted), `isActive`, timestamps.

### Xero API scopes used

`accounting.settings`, `accounting.transactions`, `accounting.contacts` — the reference-data reads use `accounting.settings`.
