# Sync Subscription Configurations from Remote

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Sync Subscription Configurations from Remote |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations Staff (internal billing admin, BillingSuperAdmin role) |
| **Business Outcome** | Enables operations staff to promote subscription configuration changes from a remote server to the current environment selectively, keeping service pricing and billing templates in sync without a full overwrite. |
| **Entry Point / Surface** | Sleek Billings App > Billing > Subscription Config > "Sync configurations from remote server" button |
| **Short Description** | Operations staff fetch pending create/update/delete changes from a configured remote server, preview them grouped by change type with JSON diffs, cherry-pick individual changes via checkbox, and apply the chosen subset. A separate "View sync logs" button surfaces an audit trail of past sync actions. Applied changes are also propagated to Xero. |
| **Variants / Markets** | SG, HK, AU (service types and priority labels span all three; client type scoping: `main`, `manage_service`, `all`) |
| **Dependencies / Related Flows** | Subscription Config list view (same page); Xero item sync on create/update/delete; Audit Logs service for sync trail; client type scoping; `SERVICE_SYNC_API` and `SERVICE_SYNC_AUTH_TOKEN` env config |
| **Service / Repository** | sleek-billings-frontend (UI); sleek-billings-backend (API owner: `src/subscriptions-config/`) |
| **DB - Collections** | MongoDB: `services` (local subscription config records), `servicehistories` (field-level change log), `auditlogs` (sync operation audit trail with tags `sync-changes-services`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Are markets scoped per environment instance or via clientType only? 2. Is the remote server always a lower environment (SIT → prod) or can it be a sibling market server? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files

**Frontend (`sleek-billings-frontend`)**
- `src/pages/SubscriptionConfig/SubscriptionConfigList.jsx` — primary UI; full sync flow (preview dialog, selection, apply)
- `src/services/api.js` — API client wrappers for all sync-related calls

**Backend (`sleek-billings-backend`)**
- `src/subscriptions-config/controllers/subscription-config.controller.ts` — REST controller, `@GroupAuth(Group.BillingSuperAdmin)` on all write endpoints
- `src/subscriptions-config/services/service.service.ts` — `getServiceChanges`, `syncServicesChanges`, `getServiceChangesLogs`
- `src/subscriptions-config/models/service.schema.ts` — `services` MongoDB collection
- `src/subscriptions-config/models/service-history.schema.ts` — `servicehistories` collection

### API endpoints (confirmed in backend controller)

| Method | Endpoint | Guard | Purpose |
|---|---|---|---|
| `GET` | `/subscription-config/changes?clientType={clientType}` | `@Auth()` | Fetch pending changes from `SERVICE_SYNC_API` |
| `PUT` | `/subscription-config/changes/sync?clientType={clientType}` | `@Auth()` + `@GroupAuth(BillingSuperAdmin)` | Apply selected changes; body: `{ services: [{code, type}] }` |
| `GET` | `/subscription-config/sync/logs` | none | Retrieve audit log of past sync operations |
| `GET` | `/subscription-config` | `@Auth()` | List all local subscription configs (page load) |

### Sync logic (from `service.service.ts`)

1. **Preview (`getServiceChanges`)**: Calls `SERVICE_SYNC_API/subscription-config?clientType=...&source=xero` (authenticated via `SERVICE_SYNC_AUTH_TOKEN`), fetches local `services` collection, compares field-by-field using `lodash.isEqual`. Produces a diff list of `{type: create|update|delete, code, value, previousValue}`.
2. **Apply (`syncServicesChanges`)**: Filters to operator-selected changes. For each:
   - `create` → calls `createService` (writes MongoDB + Xero item)
   - `update` → calls `updateService` (writes MongoDB + Xero item)
   - `delete` → soft-deletes in MongoDB (`deleted: true`) + renames Xero item to append `- DELETED`
   - Writes audit log entry to `auditlogs` with tag `sync-changes-services` (success or error per item)
3. **Logs (`getServiceChangesLogs`)**: Queries `auditlogs` by tag `sync-changes-services`; returns `text`, `oldValue`, `newValue`, `actionBy`, `createdAt`.

### Key UI behaviours (from `SubscriptionConfigList.jsx`)
- Changes grouped into `create`, `update`, `delete` buckets with counts shown
- Each entry shows code, display name, and JSON preview of `value` / `previousValue`
- Operator can "Select all", "Clear selection", or toggle individual items
- Dialog header shows `fromServer` (the source environment URL)
- Sync logs table: log text, old value, new value, action-by email, timestamp
- "Create New Configuration" button hidden unless `localStorage.environment` is `sit` or `development`; sync button always visible in production

### Criticality rationale
Subscription configs drive pricing, billing cycles, service types, and add-on availability across the billing system. Misconfigured or partially-applied syncs could silently corrupt active subscription pricing templates — hence High criticality.
