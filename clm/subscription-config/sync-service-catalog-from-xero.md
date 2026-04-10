# Sync Service Catalog from Xero

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Sync Service Catalog from Xero |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (triggered by BillingSuperAdmin via API) |
| **Business Outcome** | Ensures the platform's billing service catalog always reflects the latest item names, prices, codes, tax types, and account codes defined in Xero, preventing billing discrepancies caused by config drift. |
| **Entry Point / Surface** | Internal API: `PUT /subscription-config/sync` (requires `BillingSuperAdmin` role); no dedicated frontend UI identified — operator-triggered |
| **Short Description** | Fetches all active Xero-sourced services from the local catalog, retrieves the corresponding items from Xero, and field-by-field compares name, price, code, tax type, and account code. Any delta is applied to the local `services` record and a `ServiceHistory` entry is written for each changed field. The service's `lastSyncedAt` timestamp is updated on any write. |
| **Variants / Markets** | Unknown — `clientType` parameter scopes the sync (e.g. `main`), but no explicit market gating found in code |
| **Dependencies / Related Flows** | Xero (external source of truth for item catalog); `XeroService.getExternalServiceList()` and `XeroService.getItems()`; `ServiceHistoryService` (change audit); `AuditLogsService` (sync operation audit); related: "Sync Subscription Configurations from Remote" (cross-environment variant of the sync pipeline) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `services` (SleekPaymentDB), `servicehistories` (SleekPaymentDB) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Is this sync triggered on a schedule (cron) or always manually by an admin? No scheduler evidence found in these files. 2. What happens when Xero is unreachable — is there a retry or circuit-breaker? 3. The newer `syncServicesChanges` flow also cross-checks Xero via `checkXeroDifferences` — are both sync paths still in active use, or is the old `syncServices` being phased out? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/subscriptions-config/services/service.service.ts` — `syncServices()` (primary sync logic, line 689), `checkXeroDifferences()` (Xero drift detection, line 407), `compareServices()` (invokes drift check during cross-env sync, line 573)
- `src/subscriptions-config/repositories/service.repository.ts` — `ServiceRepository` backed by `SleekPaymentDB`; CRUD on `services` collection
- `src/subscriptions-config/services/service-history.service.ts` — `createServiceHistory()` wraps `ServiceHistoryRepository`; one record per changed field

### Controller endpoint
| Method | Route | Guard | Purpose |
|---|---|---|---|
| `PUT` | `/subscription-config/sync` | `@Auth()` + `@GroupAuth(BillingSuperAdmin)` | Trigger Xero → local catalog sync |

### Sync logic (`syncServices`, line 689)
1. Queries local `services` for `status=active`, `source=xero`, `clientType={param}`, `deleted=false`
2. Calls `xeroService.getExternalServiceList()` to fetch Xero items
3. For each local service, finds the matching Xero item by `externalId`
4. Compares five fields: **name**, **price**, **code**, **taxType**, **accountCode**
5. Creates a `ServiceHistory` document for each differing field (`actionType=update`)
6. Writes the updated service back via `serviceRepository.updateById()` with `lastSyncedAt = new Date()`

### Drift detection (`checkXeroDifferences`, line 407)
- Called during `compareServices()` (the cross-env sync preview flow)
- Checks the same four fields: name, price, taxType, accountCode
- Logs divergence at `info` level; does **not** auto-apply — alerts only
- Only runs for services where `source === 'xero'` and `status === 'active'`

### MongoDB schemas
- **`services`** (`service.schema.ts`): fields synced from Xero — `name`, `price`, `code`, `taxType`, `accountCode`; also `lastSyncedAt` (updated on each sync run); uniqueness index on `{code, clientType}`
- **`servicehistories`** (`service-history.schema.ts`): `referenceId` (service `_id`), `fieldName`, `previousValue`, `currentValue`, `actionType`
