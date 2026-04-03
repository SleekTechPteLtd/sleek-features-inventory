# Manage billing service catalog

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage billing service catalog |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations Admin and Finance users (Sleek group checks: `OPERATION_ADMIN`, `FINANCE`) for create, edit, clone, and delete; **Service Config Admin** (`SERVICE_CONFIG_ADMIN`) for remote sync and service logs |
| **Business Outcome** | Internal teams keep sellable services accurate per client type—codes, pricing, tiers, billing rules, display surfaces, and accounting mappings—so sales, quoting, and billing reflect the right offerings and Xero-aligned accounts where used. |
| **Entry Point / Surface** | **sleek-website** admin: **`/admin/service-configuration/`** (webpack entry `admin/service-configuration`). `AdminLayout` with `sidebarActiveMenuItemKey="services"` (see `new-admin-side-menu`: Services → this href). Blocked when Sleek Billings switch is enabled (`sleekBillingsAPI.getSleekBillingsConfig` → `SWITCH_TO_SLEEK_BILLINGS === "enabled"`). |
| **Short Description** | Lists services for a selected **Client Type** (CMS `CLIENT_TYPES`) with filters on code, source (internal vs Xero), name, duration, billing cycle, type, status, recurring, and display (admin / customer / payment request). Opens a dialog to add or edit via **`ServiceForm`**: name, short name, code (with prefix-driven defaults for type, recurring, display), optional **Purchase** and **Sell** blocks with prices, Xero account and tax mappings (`paymentApi.getXeroAccounts`, `getXeroTaxRates`), type, tier/meta, status, duration, recurring, billing cycle, test flag. **Clone** seeds a new service. **Service Config Admin** can preview changes from a remote server (`getServicesChanges`), apply sync (`syncServicesChanges`), and view sync logs (`getServicesChangesLogs`). Create/edit can be disabled by CMS `billing_configuration.disable_create_edit_new_code`. |
| **Variants / Markets** | **Unknown** in this UI (client type and CMS `billing_configuration` drive options; no explicit SG/HK/UK/AU list in these files). |
| **Dependencies / Related Flows** | **Subscription service API** (`getBaseSubscriptionServiceUrl()`): `GET/POST/PUT /services`, `GET /external-services`, `DELETE /services/:id`, `GET /services/changes`, `PUT /services/changes/sync`, `GET /services/sync/logs`. **Payment API**: Xero tax rates and accounts for the selected client type. **Main API** (`api.isMember`) for group membership. **Sleek Billings** config gate. Downstream: any flow that consumes catalogued services (subscriptions, payment requests, invoicing). |
| **Service / Repository** | **sleek-website**: `src/views/admin/service-configuration/index.js`, `service-form.js`. **External**: subscription/billing backend (service URLs from `api.js`); Xero data via payment API; CMS/platform config for `SERVICE_TYPES`, `CLIENT_TYPES`, duration/billing options, currency symbol. |
| **DB - Collections** | **Unknown** (persistence is in the subscription service and related backends; not visible in sleek-website). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether **`componentDidMount`** in `index.js` is correct: on successful `getSleekBillingsConfig` with switch **not** enabled it **`return`s early** and never loads the page; only the **`catch`** path continues—confirm intended behavior vs bug. Exact subscription-service schema and collection names. Whether **`syncServices`** in `api.js` (unused here) vs **`syncServicesChanges`** is the canonical production sync. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/service-configuration/index.js` (`AdminServicesConfigurationView`)

- Mount: **`sleekBillingsAPI.getSleekBillingsConfig`** gate; then **`getUser`**, **`getBillingConfig`** (`api.getServices(clientType)`), **`getExternalServices`**, **`getTaxRateOptions`** (`paymentApi.getXeroTaxRates`), **`getAccountsOptions`** (`paymentApi.getXeroAccounts`), platform config for **`SERVICE_TYPES`**, **`CLIENT_TYPES`**, **`billing_configuration`** (duration/billing cycle options, `disable_create_edit_new_code`).
- Permissions: **`isOperationAdminOrFinance`** → `hasUpdatePermission`; **`isServiceConfigAdmin`** → `hasSyncPermission`.
- Table columns: code, source tag (internal/Xero), name, unit price (platform currency), duration, billing cycle, type, status, recurring, display; **Edit** opens dialog with **`getCurrentServiceDetails`**; **Clone** copies details in add mode with cleared linkages.
- **`addUpdateService`**: **`api.updateServices`** vs **`api.postService`** with JSON body from form.
- **`deleteService`**: **`api.deleteService(serviceId)`**.
- Sync: **`toggleSyncDialogBox`** → **`api.getServicesChanges`**; **`syncServicesChanges`** → **`api.syncServicesChanges`**; logs → **`api.getServicesChangesLogs`**.
- External catalog picker: **`selectServiceDialogContent`** lists **`externalServicesFiltered`**, **Select** sets linked service fields (`externalId`, `linkedService`, etc.).

### `src/views/admin/service-configuration/service-form.js` (`ServiceForm`)

- Validation: required name, code, internal name, type, status, duration, recurring, billing cycle; tier requires **Meta Number**.
- **`validateForm`** builds payload: `name`, `code`, `internalName`, `type`, `status`, `duration`, `recurring`, `price`, `metaNumber`, `min`/`max`, `includedServiceIds`, `conditionalServiceIds`, `clientType`, `source` (`xero` when linked), `externalId`, `display` (filtered to `optionsAdminCustomer`), `isSold`/`isPurchased`, purchase and sale account/tax/description fields, `description`, `isTest`, optional `tier`, `billingCycle`, `_id` when editing.
- **`handleCodeChangeTextInput`**: prefix map **`codeMapping`** (e.g. `AC` → accounting), **`-RE-`/`-OT-`** segments set recurring and default **Display In** targets.
- **`handleTypeChange`**: tier enabled for `accounting`, `corporate_secretary`, `director` only.
- Conditional/included services and min/max UI exist in file but are **commented out** in `render`.

### `src/utils/api.js` (service catalog client)

- **`postService`**, **`getServices`**, **`updateServices`**, **`getExternalServices`**, **`deleteService`**, **`syncServicesChanges`**, **`getServicesChanges`**, **`getServicesChangesLogs`** — paths under **`getBaseSubscriptionServiceUrl()`** as listed in Master sheet.

### Navigation

- **`src/components/new-admin-side-menu.js`**: menu entry **`href="/admin/service-configuration/"`** under Services.

### Webpack

- **`webpack/paths.js`**: entry **`admin/service-configuration`** → **`./src/views/admin/service-configuration/index.js`**.
