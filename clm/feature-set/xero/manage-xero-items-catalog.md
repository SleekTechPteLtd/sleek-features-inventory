# Manage Xero Items Catalog

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Xero Items Catalog |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User / Admin |
| **Business Outcome** | Keeps the billable services catalog in Xero current so that invoices can reference accurate product codes, descriptions, and pricing. |
| **Entry Point / Surface** | Internal admin tooling / API — `GET /xero/items`, `POST /xero/items`, `PUT /xero/items` |
| **Short Description** | Allows authenticated users to list, create, and update service items in the connected Xero organisation. Items created here feed directly into invoice line-item selection across all subscription and billing flows. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | `getExternalServiceList()` (xero.service.ts) consumes `getItems()` and maps items to `ExternalServiceDto` used by invoice/subscription flows; Xero token management (`xero_settings` collection) must be active for API calls to succeed |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `xero_settings` (OAuth token + client credentials persistence only; item data lives in Xero) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which UI surface (admin app or internal tool) calls these endpoints — the controller has no frontend route hint; `clientType` header (`main` / `manage_service`) selects the Xero tenant — unclear whether both tenants share one catalog or maintain separate item sets per market |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `src/xero/xero.controller.ts`

| Method | Route | Guard | Notes |
|---|---|---|---|
| `GET` | `/xero/items` | `@Auth()` | Lists all items from the connected Xero tenant |
| `POST` | `/xero/items` | `@Auth()` | Creates a new item; accepts `xero-node` `Item` shape |
| `PUT` | `/xero/items` | `@Auth()` | Updates an existing item; `itemID` is required in body |

All three endpoints require a `client-type` header (`main` \| `manage_service`) to select the Xero tenant.

### Service — `src/xero/services/xero.service.ts`

- `getItems()` (line 286): calls `xeroClient.accountingApi.getItems(tenantId)` → returns `Item[]`
- `createItem(itemInput)` (line 949): wraps item in `{ items: [itemInput] }`, calls `accountingApi.createItems()`; surfaces Xero `ValidationErrors` as `BadRequestException`
- `updateItem(itemInput)` (line 975): requires `itemID`; calls `accountingApi.updateItem(tenantId, itemID, items)`; same validation error surfacing
- `getExternalServiceList()` (line 1041): downstream consumer — calls `getItems()` and maps to `ExternalServiceDto` `{ id, code, name, description, price, taxType, accountCode }` for use in subscription/invoice selection flows

Token refresh is handled automatically via `ensureTokenIsRefresh()` before each API call. Daily rate-limit errors flip `xero_settings.isActive = false` and switch to the backup token.

### DTO — `src/xero/dtos/xero.item.dto.ts`

`ItemDto` carries `itemID` (required), `email`, `firstName`, `lastName` — primarily used for contact lookups rather than item payloads; the items endpoints accept the raw `xero-node` `Item` type directly.

### DB schema — `src/xero/models/xero-setting.schema.ts`

Collection `xero_settings` stores encrypted OAuth tokens (`value`), `clientId`, `clientSecret`, and an `isActive` flag. Items themselves are not stored locally.
