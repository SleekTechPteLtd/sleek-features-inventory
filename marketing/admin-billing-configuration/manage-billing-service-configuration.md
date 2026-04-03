# Manage billing service configuration

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage billing service configuration |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations staff (browse, filter, paginate); **Operation Admin** group members (edit and persist updates) |
| **Business Outcome** | The Xero-linked service catalogue stays consistent with billing rules and with where services appear in the admin and customer apps. |
| **Entry Point / Surface** | **sleek-website** Sleek Admin: **Billing configuration** page at `/admin/billing-configuration/` (`sidebarActiveMenuItemKey="billing-configuration"`, webpack entry `admin/billing-configuration`). |
| **Short Description** | Loads Xero-aligned billing rows per **client type** (from CMS `CLIENT_TYPES`). Staff filter by Xero code, service name, duration, billing cycle, service type, Xero status, recurring, and optional **Display in Admin app** / **Display in Customer app** (when enabled via CMS `billing_configuration` flags). Results are **client-side paginated**. Operation Admins enter edit mode to change duration, billing cycle, service type, Xero status, recurring, and visibility flags, then **update** to POST changed rows to the marketing API. |
| **Variants / Markets** | Unknown — client types and options are driven by CMS platform config rather than hard-coded regions in this view. |
| **Dependencies / Related Flows** | **Marketing API** (sleek-website base URL): `GET` / `POST` `${getBaseUrl()}/admin/billing-config/:clientType` via `api.getBillingConfig` / `api.updateBillingConfig`. **CMS / platform config**: `getPlatformConfig()` → `billing_configuration` (options for duration, billing cycle, feature flags `display_in_admin` / `display_in_customer`), `admin_constants` → `SERVICE_TYPES`, `CLIENT_TYPES`. **Auth**: `api.isMember({ group_name: SLEEK_GROUP_NAMES.OPERATION_ADMIN })` for edit permission. Downstream: any flow that prices or surfaces services using this catalogue (company billing, subscriptions, payment requests). |
| **Service / Repository** | **sleek-website**: `src/views/admin/billing-configuration/index.js`, `src/utils/api.js` (`getBillingConfig`, `updateBillingConfig`, `getUser`, `isMember`). |
| **DB - Collections** | Unknown — persistence is behind the marketing API; not visible in this repo. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which backend service owns `/admin/billing-config` and how it syncs with Xero; whether `options_billing_cyle` typo in CMS key is intentional legacy. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/billing-configuration/index.js`

- **Layout**: `AdminLayout` with `hideDrawer={true}`, title **Billing configuration**.
- **Data load**: `componentDidMount` → `getUser()`, `getBillingConfig()`, then `getPlatformConfig()` for `SERVICE_TYPES`, `CLIENT_TYPES`, `billing_configuration` (duration/cycle options, `display_in_admin` / `display_in_customer` toggles), `hasUpdatePermission` from `isOperationAdmin()` → `api.isMember({ group_name: SLEEK_GROUP_NAMES.OPERATION_ADMIN })`.
- **Read API**: `getBillingConfig(clientType)` maps `response.data.xeroItems` into table state and builds `serviceNameFilter` / `xeroCodeFilter` option lists.
- **Filters**: `FilterSelect` for `xero_code` and `description`; `MultiFilerSelect` for `duration`, `billing_cycle`, `service_type`, `xero_status`, `recurring`, optional `display_in_admin`, `display_in_customer`. Logic in `filterList` / `multiFilterConfig` / `multiFilter` — filters apply to `searchXeroItems` then paginated slice.
- **Pagination**: `Pagination` component; `handleChangePage`, `handleChangeRowsPerPage`; page size options `[10, 20, 50]`.
- **Edit mode**: `toggleEditMode` — **edit page** shows `CustomSelect` per editable field; **update** calls `updateBillingConfig` with `updateItems` accumulated in `saveToUpdateItems` / `assignValue`. Cancel restores `xeroItemsOrig`.
- **Write API**: `api.updateBillingConfig(clientType, { body: JSON.stringify(updateItems) })` then refresh via `getBillingConfig` and `filterList`.

### `src/utils/api.js`

- `getBillingConfig(clientType)` → `GET ${getBaseUrl()}/admin/billing-config/${clientType}` (`getResource`).
- `updateBillingConfig(clientType, options)` → `POST ${getBaseUrl()}/admin/billing-config/${clientType}` (`postResource`).

### `src/utils/constants.js`

- `SLEEK_GROUP_NAMES.OPERATION_ADMIN: "Operation Admin"` — used for update permission check.

### Webpack

- Entry `admin/billing-configuration` → `./src/views/admin/billing-configuration/index.js`; output `admin/billing-configuration/index.html`.
