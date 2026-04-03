# Review paid subscription transaction details

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Review paid subscription transaction details |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operations staff can confirm who owns the subscription, which internal roles are assigned, and how each billed service was paid—without leaving admin. |
| **Entry Point / Surface** | Sleek Admin > Subscriptions > Paid subscriptions — open “Transaction Details” for a company subscription (URL `/admin/subscriptions/new/details/?subscriptionId=…`, also linked from the paid-subscriptions table) |
| **Short Description** | Loads a single company subscription by id, resolves CSS-in-charge and account manager from company resource allocation, shows the company owner, then renders one card per active service with invoice number (link to invoice URL), payment status (Success / Failed / Processing), duration and renewal date, and whether payment was card vs manual (with a popover for manual payment metadata). Subscription display names come from CMS `SUBSCRIPTION_NAMES`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: admin paid-subscriptions list (`/admin/subscriptions/new/`) linking to this page; CMS `admin_constants` / `SUBSCRIPTION_NAMES` for labels. APIs: `GET /admin/company-subscriptions/:subscriptionId`, `GET /companies/:companyId/company-resource-allocation` (resource types `css-in-charge`, `accounting-manager`). Related UI: company edit (`/admin/companies/edit/?cid=`), `ManualPaymentInfo` (`views/admin/subscriptions/unpaid/manual-payment-info`). |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether all tenants expose the same subscription payload shape for `expected_external_payment_info` vs per-service invoices; backend persistence and auth for admin subscription endpoints are not visible in these view files. `invoice.js` references `classes.textWarning` without defining it in `styles`—verify runtime styling. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Page shell / data load**: `src/views/admin/subscriptions/new/details/index.js` — `AdminSubscriptionsView` uses `AdminLayout` with `sidebarActiveMenuItemKey="subscriptions"`, `sidebarActiveMenuSubItemKey="paid-subscriptions"`, `hideDrawer={true}`. `componentDidMount` calls `getUser` (from `../../common`), `fetchSubscriptionInfo`, and loads `getPlatformConfig()` then `SUBSCRIPTION_NAMES` from `cmsGeneralFeatureList` → `admin_constants.props`. `fetchSubscriptionInfo` reads `subscriptionId` from the query string and calls `api.getAdminCompanySubscription(subscriptionId)` (`GET ${base}/admin/company-subscriptions/${subscriptionId}`). `fetchCompanyResourceAllocation` uses `api.getCompanyResourceAllocation(companyId)` (`GET ${base}/companies/${companyId}/company-resource-allocation`), then `lodash/find` for `CSS_IN_CHARGE_RESOURCE_TYPE = "css-in-charge"` and `ACCOUNTING_IN_CHARGE_RESOURCE_TYPE = "accounting-manager"`.
- **People row**: Table columns “CSS in charge”, “Account Manager”, “Owner” — names from `get(this.state.cssInCharge, "user")`, `get(this.state.accountingInCharge, "user")`, and `get(this.state.subscription, "companyAdmin")` via `getOwnerName` / `getNameInCharge`.
- **Per-service invoice UI**: `renderBodyContent` maps `subscription.services` to `<Invoice success={true} subscription={…} service={…} subscriptionLabels={…} />`. Unused: `renderExpectedExternalPayment` (would render `<Invoice subscription={…} />` when `expected_external_payment_info` exists) is not called from `render`—the active path is always the per-service map.
- **Invoice component**: `src/views/admin/subscriptions/new/details/components/invoice.js` — `getInvoiceNo` / `getInvoiceUrl` prefer `service.expected_pay_at` branch (`invoices[0]`) vs single `service.invoice`. Renders invoice number as external `Link` to invoice URL, company name, status text from `getServiceStatus` (`service.invoice.status` → done/failed/default → Success/Failed/Processing), color classes for success/danger. Embeds `History`.
- **History table**: `src/views/admin/subscriptions/new/details/components/history.js` — columns Subscription Name (CMS label via `subscriptionLabels` and `subscription.service`), Duration (months), Renewal Date (`service.end_at` formatted), Payment Info — `isManualPaymentMade` distinguishes instant card/cash vs external/company expected payment flows; optional `Popover` with `ManualPaymentInfo` for manual path. `getInvoiceInfo` merges invoice from `service.invoice`, `subscription.expected_external_payment_info`, or `company.expected_external_payment_info` (note: one branch sets `expected_pay_at` from `company_expected_external_payment_info` while reading `company.expected_external_payment_info.invoices.0`—possible typo in property names worth backend alignment).
- **Webpack**: `webpack/paths.js` entry `admin/subscriptions/new/details/index`; `webpack.common.js` emits `admin/subscriptions/new/details/index.html`.
