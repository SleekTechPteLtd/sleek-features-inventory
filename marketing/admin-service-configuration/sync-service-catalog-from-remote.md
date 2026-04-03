# Sync service catalog from remote

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Sync service catalog from remote |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Service Config Admin (Sleek group `SERVICE_CONFIG_ADMIN` / `"Service Config Admin"`) |
| **Business Outcome** | Service configuration admins compare pending remote deltas, apply them into this environment’s catalog for the selected client type, and review who synced what and when so the local service list stays aligned with the subscription service’s remote source of truth. |
| **Entry Point / Surface** | Sleek Admin → **Service configuration** — `/admin/service-configuration/` (`AdminServicesConfigurationView`, sidebar key `services`). Sync controls render only when `hasSyncPermission` is true. Same page is unavailable when Sleek Billings switch is enabled (`getSleekBillingsConfig` → `SWITCH_TO_SLEEK_BILLINGS === "enabled"`). |
| **Short Description** | **Service logs** opens a dialog that loads historical entries via `getServicesChangesLogs` and lists log text, actor email, and timestamp. **Sync services from remote server** fetches a pending diff with `getServicesChanges` for the current **Client Type**, shows counts of create/update/delete operations, the originating server label (`fromServer`), and full JSON in a confirmation dialog; confirming calls `syncServicesChanges`, then refreshes the local table with `getBillingConfig`. |
| **Variants / Markets** | Unknown (scoped by client type and environment; no market list in these files). |
| **Dependencies / Related Flows** | **Subscription service HTTP API** (`getBaseSubscriptionServiceUrl()`): `GET /services/changes?clientType=`, `PUT /services/changes/sync?clientType=`, `GET /services/sync/logs`. After sync, catalog reload uses `GET /services?clientType=` like the rest of the page. **Related inventory**: `manage-billing-service-catalog.md` (full service-configuration surface). **Group check**: `api.isMember` with `group_name: SLEEK_GROUP_NAMES.SERVICE_CONFIG_ADMIN`. |
| **Service / Repository** | **sleek-website**: `src/views/admin/service-configuration/index.js`; `src/utils/api.js` (`getServicesChanges`, `syncServicesChanges`, `getServicesChangesLogs`). **External**: subscription/billing backend behind `SUBSCRIPTION_API` / default host. |
| **DB - Collections** | Unknown (service definitions and sync logs persisted by the subscription service; not defined in sleek-website). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact semantics of “remote” vs `fromServer` (hostname/label only in API payload). Whether `syncServices` (`PUT /services/sync`) remains in use elsewhere vs `syncServicesChanges` as the admin-approved path. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/service-configuration/index.js`

- **Permission:** `isServiceConfigAdmin` → `api.isMember({ query: { group_name: SLEEK_GROUP_NAMES.SERVICE_CONFIG_ADMIN } })`; result stored as `hasSyncPermission` (constructor state and `componentDidMount`, ~lines 407–415, 876–882).
- **UI:** When `hasSyncPermission`, header actions **service logs** (`toggleSyncLogsDialogBox`) and **sync services from remote server** (`toggleSyncDialogBox`) (~506–528).
- **Pending diff:** `toggleSyncDialogBox` awaits `api.getServicesChanges(clientType)` and sets `dataChangesJSON` for **Sync Service Confirmation** dialog (~1205–1210). `syncServiceDialogContent` shows `fromServer`, CREATE/UPDATE/DELETE counts, confirmation copy, and `JSON.stringify` of the payload (~1118–1133).
- **Apply:** Dialog primary action `syncServicesChanges` → `api.syncServicesChanges(clientType)`, then `getBillingConfig()` and closes dialog (~1264–1269).
- **Logs:** `toggleSyncLogsDialogBox` awaits `api.getServicesChangesLogs()` → `dataChangesLogsJSON`; `syncServiceLogsDialogContent` table columns: `log.text`, `log.actionBy.email`, `formatDate(log.createdAt, ...)` (~1213–1218, 1136–1167).
- **Dialogs:** `dialogSyncIsOpen` / `dialogSyncLogsIsOpen` wired to `Dialog` components (~784–839).

### `src/utils/api.js`

- `getServicesChanges(clientType)`: `GET ${getBaseSubscriptionServiceUrl()}/services/changes?clientType=${clientType}` (~2001–2003).
- `syncServicesChanges(clientType)`: `PUT ${getBaseSubscriptionServiceUrl()}/services/changes/sync?clientType=${clientType}` (~1996–1998).
- `getServicesChangesLogs()`: `GET ${getBaseSubscriptionServiceUrl()}/services/sync/logs` (~2006–2007).
- Base URL: `getBaseSubscriptionServiceUrl()` — `process.env.SUBSCRIPTION_API` or dev `http://localhost:3010` / prod `https://api.sleek.sg` (~29–37).

### Navigation and gating

- **Menu:** `src/components/new-admin-side-menu.js` — **Service configuration** → `href="/admin/service-configuration/"`, shown when `service_configuration.enabled && !sleekBillingsEnabled` (~1034–1048).
- **Page gate:** `componentDidMount` early exit when Sleek Billings config enables switch (~847–853).

### Webpack

- **`webpack/paths.js`**: entry `admin/service-configuration` → `./src/views/admin/service-configuration/index.js`.
