# Review Subscription Config Sync Audit Trail

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Review subscription config sync audit trail |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables operations staff to trace and verify every subscription configuration change synced from a remote server, supporting accountability and debugging of past sync operations. |
| **Entry Point / Surface** | sleek-billings-frontend > Subscription Configurations > "View sync logs" button |
| **Short Description** | Operations staff click "View sync logs" on the Subscription Configurations list page to open a modal table showing all past sync actions: a log description, old value, new value, the email of the user who performed the action, and the date/time. Data is fetched from an external Sleek Auditor service, filtered by the `sync-changes-services` tag. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Sync subscription configs from remote server (upstream action that generates log entries); Subscription Config list page (`/subscription-config`); Sleek Auditor external service (log storage and retrieval) |
| **Service / Repository** | sleek-billings-frontend (UI); sleek-billings-backend (`sleek-clm-monorepo/apps/sleek-billings-backend`) for `GET /subscription-config/sync/logs` |
| **DB - Collections** | Audit log records stored in external Sleek Auditor service (not a local MongoDB collection); local `servicehistories` collection stores field-level history per service config record |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `GET /subscription-config/sync/logs` has no `@Auth()` or `@GroupAuth()` decorator unlike all other endpoints in the same controller — this endpoint appears unauthenticated and may be an oversight; logs are returned all at once with no pagination — unclear if this could be a performance issue as log volume grows; markets not determinable from code alone |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Frontend file
`sleek-clm-monorepo/apps/sleek-billings-frontend/src/pages/SubscriptionConfig/SubscriptionConfigList.jsx`

- `handleGetSyncLogs()` calls `sleekBillingsApi.getSubscriptionConfigSyncLogs()` → `GET /subscription-config/sync/logs`
- Response stored in `logs` state; opens `openLogsDialog` (MUI `Dialog`, `maxWidth="md" fullWidth`, title "Sync Logs")
- Renders a MUI `Table` with columns: Logs (text), Old Value, New Value, Action By (email), Date & Time
- Values that are `null`, `undefined`, or empty objects rendered as `—`; objects rendered as formatted JSON in a `<pre>` block
- Empty state: "No logs found."

### API service
`sleek-clm-monorepo/apps/sleek-billings-frontend/src/services/api.js`
```js
getSubscriptionConfigSyncLogs: async () => {
  const response = await api.get(`/subscription-config/sync/logs`);
  return response;
}
```

### Backend controller
`sleek-clm-monorepo/apps/sleek-billings-backend/src/subscriptions-config/controllers/subscription-config.controller.ts`
- `@Get('/sync/logs')` → `getServiceChangesLogs()` — **no `@Auth()` guard applied** (unlike all other endpoints in this controller)
- Returns `SyncLogsResponse[]`

### Backend service
`sleek-clm-monorepo/apps/sleek-billings-backend/src/subscriptions-config/services/service.service.ts`
- `getServiceChangesLogs()` calls `this.auditLogsService.getAuditLog({ tags: ['sync-changes-services'] })`
- Maps records to `SyncLogsResponse`: `{ text, actionBy, createdAt, oldValue, newValue }`
- No pagination applied — returns all records

### Audit log shape (`SyncLogsResponse` DTO)
`sleek-clm-monorepo/apps/sleek-billings-backend/src/subscriptions-config/dtos/sync-logs.response.dto.ts`
| Field | Type | Description |
|---|---|---|
| `text` | string | Human-readable description of the sync action |
| `actionBy` | `{ email: string }` | User who triggered the sync |
| `createdAt` | string (ISO date) | Timestamp of the action |
| `oldValue` | any | Previous value before the sync |
| `newValue` | any | New value applied by the sync |

### External audit log storage
`sleek-clm-monorepo/apps/sleek-billings-backend/src/audit-logs/audit-logs.service.ts`
- `addAuditLog()` POSTs to `SLEEK_AUDITOR_URL/audit-logs` with tag `sync-changes-services`
- `getAuditLog()` GETs from `SLEEK_AUDITOR_URL/audit-logs?tags[]=sync-changes-services`
- Auth via `SLEEK_AUDITOR_API_KEY` header

### Local history schema
`sleek-clm-monorepo/apps/sleek-billings-backend/src/subscriptions-config/models/service-history.schema.ts`
- Collection: `servicehistories` (inferred from class name `ServiceHistory`)
- Fields: `referenceId`, `fieldName`, `currentValue`, `previousValue`, `actionType` (create/update/delete), `deleted`, timestamps

### Audit log write path (when sync runs)
`sleek-clm-monorepo/apps/sleek-billings-backend/src/subscriptions-config/services/service.service.ts` → `syncServicesChanges()` calls `auditLogsService.addAuditLog(...)` with `tags: ['sync-changes-services']` for each create/update/delete action
