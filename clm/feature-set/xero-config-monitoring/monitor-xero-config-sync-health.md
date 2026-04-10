# Monitor Xero Config Sync Health

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Monitor Xero Config Sync Health |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators can detect and respond to Xero configuration sync failures before they impact billing or accounting workflows for any connected tenant. |
| **Entry Point / Surface** | Sleek Billings Frontend > Developer Tools > Xero Config Monitoring (`/xero-config-monitoring`) |
| **Short Description** | Displays a searchable table of all Xero tenants showing sync status, health status, last sync time, config type, sync interval, and error count. Operators use it to identify unhealthy or stale Xero integrations at a glance and take corrective action. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Xero Webhook monitoring (`/xero-webhook`); Xero tenant configuration; requires a backend API to supply per-tenant sync health data (not yet wired at time of scan) |
| **Service / Repository** | sleek-billings-frontend, sleek-clm-monorepo (apps/sleek-billings-frontend), sleek-service-delivery-api |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Low |
| **Disposition** | Unknown |
| **Open Questions** | 1. Backend API not yet connected — component uses hardcoded sample data with a "replace with actual data from your backend" comment; is this feature still in development? 2. sleek-service-delivery-api was scanned and contains no Xero-related code — which backend service is intended to supply per-tenant sync health data? 3. The row-level action menu (EllipsisVerticalIcon) renders but has no handler — what operations are planned (e.g. force re-sync, disable tenant)? 4. No market/region filtering visible — is monitoring scope global or per-market? 5. Component is duplicated verbatim in both sleek-billings-frontend and sleek-clm-monorepo — which is the canonical source? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `src/App.jsx:25` — lazy-imported as `XeroConfigMonitoringList`
- `src/App.jsx:174` — mounted at route `xero-config-monitoring`, grouped under `{/* Developer Routes */}` alongside `stripe-webhook` and `xero-webhook`; indicates this is an internal operator/developer tool

### Component: `XeroConfigMonitoringList`
- `src/pages/XeroConfigMonitoring/XeroConfigMonitoringList.jsx:4–125`
- Renders a full-page table with search input (client-side filter by `searchQuery` state)
- Table columns: Tenant ID, Tenant Name, Status, Last Sync, Config Type, Health Status, Last Checked, Sync Interval, Error Count, Actions
- Data shape per row: `{ tenantId, tenantName, status, lastSync, configType, healthStatus, lastChecked, syncInterval, errorCount }`
- Sample data shows `configType: 'Chart of Accounts'`, `syncInterval: '15 minutes'`, `healthStatus: 'HEALTHY'`, `errorCount: 0`
- Status and Health Status rendered as colour-coded badge pills (green for ACTIVE/HEALTHY)
- Row-level kebab menu button (`EllipsisVerticalIcon`) present but no click handler implemented

### Backend integration status
- `src/pages/XeroConfigMonitoring/XeroConfigMonitoringList.jsx:8` — comment: `// Sample data - replace with actual data from your backend`
- No `useEffect`, `fetch`, Axios, or API hook calls present — data is entirely static at time of scan
- No error or loading states implemented

### Related pages in the same developer-tools group
- `src/pages/XeroWebhook/XeroWebhookList.jsx` (route `xero-webhook`) — Xero webhook event monitoring
- `src/pages/StripeWebhook/StripeWebhookList.jsx` (route `stripe-webhook`) — Stripe webhook event monitoring

### Multi-repo presence
- Component is identical in `sleek-clm-monorepo/apps/sleek-billings-frontend/src/pages/XeroConfigMonitoring/XeroConfigMonitoringList.jsx`
- `sleek-service-delivery-api/src/` was scanned — no Xero-related files found; intended backend integration not yet implemented in that repo
