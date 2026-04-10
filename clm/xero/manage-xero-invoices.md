# Manage Xero Invoices

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Xero Invoices |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | SuperAdmin (invoice/contact/settings endpoints); Authenticated internal service (items, tax rates, accounts, repeating invoices) |
| **Business Outcome** | Keeps Sleek's Xero accounting tenants in sync with billing activity by creating, updating, and managing invoices, contacts, credit notes, payments, and recurring invoice templates — maintaining accurate financial records in Xero. |
| **Entry Point / Surface** | Internal REST API (`/xero/*`) — no direct frontend surface; called by internal billing services and SuperAdmin tooling |
| **Short Description** | Provides a NestJS REST façade over the Xero Accounting API for two tenants (`main` and `manageService`). SuperAdmins can create/update invoices and contacts and toggle the active OAuth token set; authenticated internal callers can read chart-of-accounts, tax rates, and product items, and update repeating invoice templates. |
| **Variants / Markets** | SG, HK, UK, AU (SG additionally syncs contact postal addresses to Xero) |
| **Dependencies / Related Flows** | Xero OAuth token management (XeroSetting collection); payment processing flow (markInvoiceAsPaid, createBankTransactionFee called internally); credit-note flow; subscription/billing service; Redis cache (tax rates, 24 h TTL); `@sleek-sdk/sleek-cms` (AppFeatureService); `@sleek-sdk/common` (DataStreamerService, LoggerService) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `xero-settings` (SleekXeroDB) — stores encrypted OAuth token sets, client credentials, and active/backup token state |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Who triggers `POST /xero/invoice` in practice — a manual admin script or an automated billing pipeline? 2. Is `manageService` tenant used for a specific market or product line? 3. The `PUT /xero/repeating-invoices` route has `@Param('externalId')` declared but the controller path template has no `:externalId` segment — likely a bug or dead endpoint. 4. Daily-limit fallback to backup token (setBackupIfDailyLimit) — is there an alerting mechanism when this triggers? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `src/xero/xero.controller.ts`

| Method | Route | Guard | Service call |
|---|---|---|---|
| POST | `/xero/invoice` | `@GroupAuth(SuperAdmin)` | `xeroService.updateOrCreateInvoice()` |
| POST | `/xero/contact` | `@GroupAuth(SuperAdmin)` | `xeroService.createContact()` |
| GET | `/xero/items` | `@Auth()` | `xeroService.getItems()` |
| PUT | `/xero/settings` | `@GroupAuth(SuperAdmin)` | `xeroService.updateXeroSetting()` |
| GET | `/xero/tax-rates` | `@Auth()` | `xeroService.getTaxRates()` |
| GET | `/xero/accounts` | `@Auth()` | `xeroService.getAccounts()` |
| POST | `/xero/items` | `@Auth()` | `xeroService.createItem()` |
| PUT | `/xero/items` | `@Auth()` | `xeroService.updateItem()` |
| PUT | `/xero/repeating-invoices` | `@Auth()` | `xeroService.updateRepeatingInvoice()` |

### Service — `src/xero/services/xero.service.ts`

Key capabilities:
- **`init()`** — selects `main` or `manageService` Xero tenant; decrypts stored OAuth credentials from `xero-settings`; constructs `XeroClient` with scopes `accounting.settings`, `accounting.transactions`, `accounting.contacts`.
- **`ensureTokenIsRefresh()`** — checks token expiry with a configurable buffer (`XERO_TOKEN_REFRESH_BUFFER_SECONDS`, default 300 s); retries refresh up to 3× with jittered delays (200/500/1200 ms) for retryable errors; reloads token from DB between retries to avoid concurrent-refresh conflicts.
- **`updateOrCreateInvoice()`** — calls `xeroClient.accountingApi.updateOrCreateInvoices()`; logs Xero rate-limit headers (`x-appminlimit-remaining`, `x-minlimit-remaining`, `x-daylimit-remaining`).
- **`updateInvoice()`** — calls `xeroClient.accountingApi.updateInvoice()`.
- **`createContact()` / `updateOrCreateContact()`** — upserts contact; for SG platform adds postal address (`COUNTRY_SPECIFIC_CONFIG.xero_contact_address`).
- **`getInvoiceFromIDs()` / `getInvoiceListFromInvoiceNumbers()` / `getAllInvoices()` / `getInvoicesByPage()`** — paginated invoice reads with 2 s sleep between pages to avoid rate limits.
- **`getAllCreditNotes()` / `getCreditNotesByPage()` / `getCreditNoteFromId()` / `updateOrCreateCreditNote()`** — credit-note lifecycle.
- **`getOnlineInvoiceUrl()`** — returns Xero-hosted payment URL for an invoice.
- **`markInvoiceAsPaid()`** — creates a Xero payment; validates invoice reaches PAID status; rolls back (deletes) partial payment if amount mismatch.
- **`createBankTransactionFee()`** — records Stripe fee as a `SPEND` bank transaction against `xeroStripeContactId` and account code `404`.
- **`getTaxRates()`** — cached 24 h in Redis (`xero_tax_rates_<clientType>`); lazy Xero init on cache miss.
- **`getAccounts()`** — returns chart-of-accounts (`code`, `name`, `taxType`).
- **`createItem()` / `updateItem()`** — manages Xero product/service catalog items.
- **`updateRepeatingInvoice()`** — updates a recurring invoice template by Xero ID.
- **`updateXeroSetting()`** — toggles `isActive` on the default token set document.
- **`setBackupIfDailyLimit()`** — on Xero 429 day-limit error, marks default token as inactive so next `init()` falls through to backup token.
- **`persistToken()`** — encrypts and stores refreshed token set to `xero-settings`.

### Schema — `src/xero/models/xero-setting.schema.ts`

`XeroSetting` (collection: `xero-settings`, DB: `SleekXeroDB`):
- `_id` — token key string (e.g. `XERO-TOKEN-SET-main`, `XERO-TOKEN-SET-main-BACKUP`)
- `value` — AES-encrypted JSON token set
- `clientId` — AES-encrypted Xero client ID (overrides env var)
- `clientSecret` — AES-encrypted Xero client secret (overrides env var)
- `isActive` — controls which token set is used (default vs. backup failover)

### Multi-tenant setup

Two Xero organisations are supported via `ClientType` header:
- `main` — primary billing tenant
- `manage_service` — separate tenant for managed-service billing

Configured via env vars: `XERO_CLIENT_ID_MAIN`, `XERO_TENANT_ID_MAIN`, `XERO_BANK_ACCOUNT_ID_MAIN`, `XERO_STRIPE_CONTACT_ID_MAIN` (and `_MANAGE_SERVICE` variants).
