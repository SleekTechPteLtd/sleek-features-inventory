# Manage Billable Service Catalog

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Billable Service Catalog |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Billing Super Admin |
| **Business Outcome** | Super admins maintain the authoritative list of sellable and purchasable service definitions — including pricing, billing cycle, tax classification, and tiers — so that subscriptions, invoices, and Xero remain consistent across all markets. |
| **Entry Point / Surface** | Admin App > Subscription Config (internal billing admin panel) |
| **Short Description** | Allows Billing Super Admins to create, update, and soft-delete billable service definitions. Every write operation is mirrored to the corresponding Xero item (create/update/rename) to keep the billing source of truth in sync. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Xero (item catalog sync via XeroService), SERVICE_SYNC_API (cross-environment service comparison and promotion), AuditLogsService (change audit trail), ServiceHistoryService (field-level change log), AppFeatureService (tax calculation feature flag), Subscription Config Form (UI for write operations), Sync Subscription Configs from Remote (companion sync flow) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | services, service_histories, audit_logs |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | (1) Which admin UI surface exposes the create/update/delete forms — is it an internal admin app or a Retool/custom tool? (2) `clientType` values (`main`, `manage_service`) — how do these map to market/Xero org? (3) The `SERVICE_SYNC_API` promotes changes across environments (staging → prod?) — is this a manual admin action or part of a release process? (4) `metaNumber` is used for expense-band matching in upgrade/downgrade logic — is this always manually set by admins? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `subscriptions-config/controllers/subscription-config.controller.ts`

| Method | Route | Guard | Purpose |
|---|---|---|---|
| `GET` | `/subscription-config` | `@Auth()` | List services with rich filter params |
| `GET` | `/subscription-config/changes` | `@Auth()` | Diff local services against remote server |
| `GET` | `/subscription-config/:id` | `@Auth()` | Fetch single service detail |
| `POST` | `/subscription-config` | `@Auth() + @GroupAuth(Group.BillingSuperAdmin)` | Create a new service |
| `PUT` | `/subscription-config` | `@Auth() + @GroupAuth(Group.BillingSuperAdmin)` | Update an existing service |
| `DELETE` | `/subscription-config/:id` | `@Auth() + @GroupAuth(Group.BillingSuperAdmin)` | Soft-delete a service |
| `PUT` | `/subscription-config/sync` | `@Auth() + @GroupAuth(Group.BillingSuperAdmin)` | Pull Xero item updates into local services (legacy sync) |
| `PUT` | `/subscription-config/changes/sync` | `@Auth() + @GroupAuth(Group.BillingSuperAdmin)` | Promote selected changes from remote environment |
| `GET` | `/subscription-config/sync/logs` | none visible | Retrieve sync audit log entries |

### Service — `subscriptions-config/services/service.service.ts`

- **`createService`**: Enforces unique `code` and `internalName`; creates a Xero item via `xeroService.createItem()` (unless `externalId` already supplied); stores the returned Xero `itemID` as `externalId`.
- **`updateService`**: Auto-appends/removes `- INACTIVE` suffix from the name on status toggle; calls `xeroService.updateItem()` with price, taxType, and accountCode; throws on Xero failure.
- **`deleteService`**: Renames the Xero item to `<name>- DELETED`; soft-deletes by setting `deleted: true` in MongoDB; records a `ServiceHistory` entry.
- **`syncServices`** (legacy): Pulls live Xero item list and applies field-level diffs (name, price, code, taxType, accountCode) back to local records; records each change in `ServiceHistory`.
- **`syncServicesChanges`**: Fetches services from `SERVICE_SYNC_API` (authenticated via `SERVICE_SYNC_AUTH_TOKEN`), diffs against local, and applies create/update/delete operations; logs each outcome to `AuditLogs` with `sync-changes-services` tag.
- **`calculateTAX`**: Uses `AppFeatureService` (`billing-service` / `taxCalculation` flag) to compute tax amount on a service price.
- **`buildXeroItem`**: Maps DTO fields → Xero `Item` shape (salesDetails: unitPrice, accountCode, taxType; purchaseDetails: purchasePrice, purchaseAccountCode, purchaseTaxType).

### Schema — `subscriptions-config/models/service.schema.ts`

**Collection**: `services`

Key fields:
- `name`, `code` (unique per `clientType`), `internalName` (unique per active status + `clientType`)
- `type` (ServiceType enum), `subType`, `tier` (ServiceTier enum — many accounting tiers: accounting, accounting-pro, accounting-premium, accounting-tax, etc.)
- `billingCycle`: `calendar_year` | `financial_year` | `monthly`
- `price`, `taxType`, `accountCode`, `description` (sales details)
- `isPurchased`, `purchasePrice`, `purchaseTaxType`, `purchaseAccountCode`, `purchaseDescription`
- `status`: `active` | `inactive`
- `source`: `xero` | `null`
- `externalId`: Xero itemID
- `display`: array of `customer` | `admin` | `paymentRequest`
- `includedServiceIds`, `conditionalServiceIds`, `requiredFeeIds` (self-referential relations)
- `tags`, `serviceDeliverables`, `revenueNature`, `subscriptionAddons`
- `metaNumber`: numeric threshold for expense-band tier matching
- `deleted` (soft-delete), `lastSyncedAt`, `isTest`

Indexes: `(code, clientType)` unique; `(internalName, clientType)` partial unique on active; `(type, tier, metaNumber)` for plan-matching queries.

### DTOs

- **`CreateServiceRequestDto`**: Requires `name`, `code`, `internalName`, `type`, `clientType`, `duration`, `recurring`, `price`, `isSold`, `isPurchased`, `status`, `serviceDeliverables`, `display`. Optional: `billingCycle`, `taxType`, `accountCode`, `externalId`, `tags`, `translatedNames`, etc.
- **`UpdateServiceRequestDto`**: Same shape plus `_id`; all pricing and Xero fields updatable.
