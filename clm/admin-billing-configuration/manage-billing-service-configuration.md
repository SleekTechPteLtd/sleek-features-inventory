# Manage Billing Service Configuration

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Billing Service Configuration |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations Admin |
| **Business Outcome** | Allows Operations Admins to keep Xero-linked service pricing and billing rules accurate per client type by viewing and editing key billing parameters without a deployment. |
| **Entry Point / Surface** | Sleek Admin App > Billing Configuration (sidebar key: `billing-configuration`) |
| **Short Description** | Displays a paginated table of Xero service items per client type, with inline editing for duration, billing cycle, service type, Xero status, recurring flag, and app visibility (admin/customer). Changes are batch-submitted via a single update call. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Xero (xero_code, xero_status, unit_price as source of truth); CMS platform config (SERVICE_TYPES, CLIENT_TYPES, options_duration, options_billing_cycle, display_in_admin/display_in_customer feature flags); `api.isMember` group check for Operation Admin gate; `new-company-payment-request-form` consumes `getBillingConfig` |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown (frontend only; backend endpoint is `GET/POST /admin/billing-config/:clientType`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which backend service/repo owns the `/admin/billing-config/:clientType` endpoint? Which MongoDB collections back the billing config data? What markets/jurisdictions does this cover (SG, HK, AU, UK)? Is `display_in_customer` column live in all environments or still feature-flagged off? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `src/views/admin/billing-configuration/index.js` — `AdminBillingConfigurationView` React component, rendered into `#root`
- Sidebar active key: `billing-configuration`

### Authorization
- `isOperationAdmin()` (line 272): calls `api.isMember({ group_name: SLEEK_GROUP_NAMES.OPERATION_ADMIN })` — only members of the `"Operation Admin"` group see the Edit button and can submit updates
- `SLEEK_GROUP_NAMES.OPERATION_ADMIN = "Operation Admin"` (`src/utils/constants.js:1598`)

### API surface
- `GET  /admin/billing-config/:clientType` → `api.getBillingConfig(clientType)` — fetches all Xero items for the selected client type
- `POST /admin/billing-config/:clientType` → `api.updateBillingConfig(clientType, { body })` — submits the batch of changed Xero items
- Both defined in `src/utils/api.js:1954–1964`

### Editable fields (per Xero item)
| Field | Options source |
|---|---|
| `duration` | `billing_configuration.value.options_duration` (CMS platform config) |
| `billing_cycle` | `billing_configuration.value.options_billing_cyle` (CMS platform config) |
| `service_type` | `admin_constants.SERVICE_TYPES` (CMS platform config) |
| `xero_status` | hardcoded: Active / Inactive |
| `recurring` | hardcoded: Yes / No |
| `display_in_admin` | feature-flagged (`billing_configuration.props.display_in_admin.enabled`) |
| `display_in_customer` | feature-flagged (`billing_configuration.props.display_in_customer.enabled`) |

### Read-only fields shown in view mode
- `xero_code`, `description`, `unit_price` (formatted as `$x.xx`)

### Platform config integration
- `getPlatformConfig()` supplies `cmsGeneralFeatureList` (for SERVICE_TYPES, CLIENT_TYPES) and `cmsAppFeatures` (for `billing_configuration` feature block including duration/billing-cycle option lists and column visibility flags)

### Downstream consumers
- `src/components/new-company-payment-request-form.js:221` — calls `getBillingConfig(clientType)` when building a new payment request, meaning changes here directly affect pricing options shown to customers
