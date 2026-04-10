# Review Subscription Transaction Details

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Review Subscription Transaction Details |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Gives admins a single-page view of a subscription transaction so they can confirm the assigned CSS and account manager, check per-service invoice status, verify service duration and renewal dates, and identify whether payment was made by credit card or manual/cheque. |
| **Entry Point / Surface** | Admin Panel > Subscriptions (Paid) > [Company Name] > Transaction Details |
| **Short Description** | Displays a transaction details page for a specific company subscription. Shows the CSS in charge, account manager, and company owner at the top, then renders one invoice card per service with invoice number (linked to Xero), payment status (Success / Failed / Processing), subscription name, duration (months), renewal date, and payment method (credit card or manual with cheque/tentative-date popover). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Company Resource Allocation (CSS/accounting-manager assignment); Xero (invoice URLs and invoice numbers); Admin Subscriptions list (`/admin/subscriptions/new/`); Manual Payment Info flow (`admin-subscriptions-unpaid`); Platform config (`admin_constants.SUBSCRIPTION_NAMES`) |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown (frontend only; backend serves `/admin/company-subscriptions/:id` and `/companies/:id/company-resource-allocation`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which backend service/repo handles `GET /admin/company-subscriptions/:id`? Are markets differentiated anywhere (e.g. SG vs HK cheque handling)? The `history.js` table is titled "History" but contains current service state — is historical payment history planned or was the name carried over? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/views/admin/subscriptions/new/details/index.js` — root component `AdminSubscriptionsView`; fetches subscription and resource allocation on mount; renders CSS in charge, account manager, owner header row and one `<Invoice>` card per service in `subscription.services`
- `src/views/admin/subscriptions/new/details/components/invoice.js` — `Invoice` component; shows invoice number (linked via `invoices.0.url` or `invoice.url`), per-service payment status derived from `service.invoice.status` (`done` → Success, `failed` → Failed, else Processing); delegates service-row detail to `<History>`
- `src/views/admin/subscriptions/new/details/components/history.js` — `History` component; renders table: Subscription Name, Duration, Renewal Date (`service.end_at`), Payment Info; payment method logic: `invoice.payment_method == "instant_card" || "cash"` → Credit Card, otherwise checks `subscription.expected_external_payment_info` or `company.expected_external_payment_info` → Manual Payment with popover
- `src/views/admin/subscriptions/unpaid/manual-payment-info.js` — `ManualPaymentInfo` popover; shows invoice number (Xero link), tentative payment date (`expected_pay_at`), cheque number

### API calls
| Call | Endpoint | Purpose |
|---|---|---|
| `api.getAdminCompanySubscription(subscriptionId)` | `GET /admin/company-subscriptions/:id` | Fetch full subscription with services, invoice data, company info |
| `api.getCompanyResourceAllocation(companyId)` | `GET /companies/:id/company-resource-allocation` | Fetch CSS in charge (`css-in-charge`) and accounting manager (`accounting-manager`) resource assignments |

### Key data paths accessed
- `subscription.company.name` / `subscription.company._id`
- `subscription.companyAdmin.first_name` / `last_name`
- `subscription.services[]` — array of per-service objects
- `service.invoice.status` / `.number` / `.url` / `.payment_method`
- `service.invoices[0].number` / `.url` (alternate invoice path when `expected_pay_at` present)
- `service.duration` / `service.end_at`
- `subscription.expected_external_payment_info.expected_pay_at` / `.cheque_number` / `.invoices[0]`
- Resource allocation: `resource.type` (`css-in-charge` | `accounting-manager`), `resource.user`
- Platform config: `admin_constants.SUBSCRIPTION_NAMES` (label lookup for service type)

### External integrations
- **Xero** — invoice URLs (`invoice.url`, `invoices.0.url`) linked directly in the UI
