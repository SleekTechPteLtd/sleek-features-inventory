# Promote Service Config Across Environments

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Promote service config across environments |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Billing Super Admin |
| **Business Outcome** | Enables billing super admins to keep service catalogs consistent across environments by comparing the local service catalog against a remote environment and selectively promoting creates, updates, and deletes — preventing pricing and service-definition drift between staging and production. |
| **Entry Point / Surface** | API: `GET /subscription-config/changes`, `PUT /subscription-config/changes/sync`, `GET /subscription-config/sync/logs` (consumed by Sleek Billings frontend, Subscription Config page) |
| **Short Description** | The backend fetches all service definitions from the remote environment configured via `SERVICE_SYNC_API`, compares them against the local `services` collection, and returns a diff of `create`, `update`, and `delete` operations. Super admins can selectively apply a subset of those changes; each operation is mirrored to Xero (item create/update/archive) and written to the sleek-auditor external audit log under the `sync-changes-services` tag. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Xero (item create/update/archive on every applied change); sleek-auditor external service (audit log writes and reads tagged `sync-changes-services`); remote billing backend at `SERVICE_SYNC_API` (inter-service HTTP call with `SERVICE_SYNC_AUTH_TOKEN`); Manage Subscription Configurations (same module, CRUD base) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `services` (MongoDB, Service schema — read for diff and write for applies) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which environment does `SERVICE_SYNC_API` point to in production (SIT→prod, or configurable per deployment)? 2. Is the frontend `localStorage.environment` guard the only protection against accidental direct-create in non-SIT environments, or is there also a backend guard? 3. Are there market/region-specific considerations for the `clientType` scoping (`main`, `manage_service`, `all`)? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Key files

| File | Role |
|---|---|
| `src/subscriptions-config/controllers/subscription-config.controller.ts` | Route definitions; auth guards |
| `src/subscriptions-config/services/service.service.ts` | Core diff and apply logic |
| `src/subscriptions-config/dtos/sync-services-changes.request.dto.ts` | Request shape for selective apply |
| `src/subscriptions-config/dtos/changes-services.response.dto.ts` | Diff response shape (type, code, previousValue, value) |
| `src/subscriptions-config/dtos/sync-logs.response.dto.ts` | Audit log response shape |

### API endpoints (backend)

| Method | Route | Guard | Purpose |
|---|---|---|---|
| `GET` | `/subscription-config/changes` | `@Auth()` | Fetch diff between local and remote |
| `PUT` | `/subscription-config/changes/sync` | `@Auth()` + `@GroupAuth(BillingSuperAdmin)` | Selectively apply chosen changes |
| `GET` | `/subscription-config/sync/logs` | none declared | Retrieve past sync audit log entries |

### Diff logic (`compareServices`, `service.service.ts:573`)
- Calls `SERVICE_SYNC_API/subscription-config?clientType=…&source=xero&load[]=includedServices&load[]=conditionalServices` with bearer token `SERVICE_SYNC_AUTH_TOKEN`.
- Normalizes both sides via `formatServices()` (resolves `includedServices`/`conditionalServices` refs to plain codes for portable comparison).
- Remote services present locally → `update` (field-level diff) or no-op.
- Remote services absent locally → `create`.
- Local services absent from remote → `delete`.
- Services with `isTest: true` are skipped on both sides.

### Apply logic (`syncServicesChanges`, `service.service.ts:437`)
- Accepts optional `SyncServicesChangesRequestDto.services[]` (code + type pairs) to cherry-pick; omitting it applies all diff items.
- For `create`: calls `this.createService()` which also creates the Xero item.
- For `update`: merges remote fields onto the current local document and calls `this.updateService()` which also updates the Xero item.
- For `delete`: soft-deletes the local document (`deleted: true`) and renames the Xero item with `- DELETED` suffix.
- Per-item errors are caught and logged to sleek-auditor (tag `sync-changes-services-error`) without aborting the remaining batch.
- Each successful operation writes an audit log entry to sleek-auditor: action `create`/`update`/`delete`, text `Sync successful: {code} - services changes from {fromServer}`, tagged `sync-changes-services`.

### Audit log retrieval (`getServiceChangesLogs`, `service.service.ts:389`)
- Queries sleek-auditor via HTTP `GET SLEEK_AUDITOR_URL/audit-logs?tags[]=sync-changes-services`.
- Returns: `text`, `actionBy` (user email), `createdAt`, `oldValue`, `newValue`.

### External integrations
- **Xero**: `xeroService.init({ clientType })` → `createItem` / `updateItem` called for every applied create or update; item renamed `- DELETED` on delete. Xero sync failure throws `BadRequestException` and aborts that item.
- **sleek-auditor**: All sync outcomes (success and error) are written via `auditLogsService.addAuditLog()` which POSTs to `SLEEK_AUDITOR_URL/audit-logs` with retry logic.

### Auth
- `GET /changes` and `GET /sync/logs` — authenticated users.
- `PUT /changes/sync` — restricted to `Group.BillingSuperAdmin`.
