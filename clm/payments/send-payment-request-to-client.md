# Send Payment Request to Client

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Send payment request to client |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations Staff |
| **Business Outcome** | Operations staff can generate itemised invoices and dispatch secure payment links to company contacts, enabling clients to settle service fees online without manual billing. |
| **Entry Point / Surface** | Sleek Admin > Company Overview > Billing > Payment Request tab; also triggered from AGM/AR workflow tasks (EOT and penalties) |
| **Short Description** | Operations staff compose an itemised payment request for a company contact by selecting Xero service line items with quantities, unit prices, and optional subscription date ranges. On submission the system creates the request and sends a secure token link to the client's email for online payment. Staff can also charge a registered credit card immediately if the feature is enabled. |
| **Variants / Markets** | Unknown — currency is driven by platform config suggesting multi-market support, but no explicit market gating was found in the frontend code |
| **Dependencies / Related Flows** | Xero item catalogue (`GET /admin/payment-requests/xero-items`); credit card lookup (`getCreditCardsByCompanyId`); billing config / FYE rules (`getBillingConfig`); AGM/AR EOT penalties workflow; company subscriptions (subscription date auto-population) |
| **Service / Repository** | sleek-website (frontend); backend admin API (`/admin/payment-requests`); payment-api microservice (`payment-api.sleek.sg`) |
| **DB - Collections** | Unknown — backend not in scope; frontend payload fields indicate a `payment_requests` collection with fields: `_id`, `number`, `email`, `status`, `token_expiry_date`, `createdBy`, `services_availed` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which backend service owns and stores payment requests — is it the main API or payment-api.sleek.sg? 2. How is the secure token generated and delivered (which email service)? 3. Does `isChargeNow` trigger an immediate Stripe / card network charge, and if so through which service? 4. Are there market-specific variants (SG/HK/UK/AU) or a single flow for all markets? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/components/new-company-payment-request-form.js` — form component; handles item selection, quantity/price input, subscription date range, email validation, discount line items, and optional "charge card now" checkbox
- `src/views/admin/company-overview/billing-payment-request.js` — billing tab view; lists all payment requests for a company, manages create/view/edit modes, submits to API
- `src/utils/payment-api.js` — payment microservice utilities (coupons, invoices, subscriptions); does not contain payment request methods directly
- `src/utils/api.js` — main API utilities containing payment request functions (lines 1789–1827)
- `src/utils/constants.js:1808` — `PAYMENT_REQUEST_STATUSES`: `new`, `used`, `expired`

### API calls (from `src/utils/api.js`)
| Function | Method | Endpoint |
|---|---|---|
| `getPaymentRequests(companyId)` | GET | `/admin/{companyId}/payment-requests` |
| `postPaymentRequest(options)` | POST | `/admin/payment-requests` |
| `updatePaymentRequestStatus(id, options)` | POST | `/admin/payment-requests/{id}/change-status` |
| `getXeroItemsForPaymentRequest()` | GET | `/admin/payment-requests/xero-items` |
| `getCreditCardsByCompanyId(companyId)` | GET | (payment service) |
| `getBillingConfig(clientType)` | GET | (billing config service) |

### Payment request object shape (frontend payload)
```json
{
  "paymentRequestId": "<id or null for new>",
  "company_id": "<companyId>",
  "email": "<recipient email>",
  "services_availed": [
    {
      "service_code": "...",
      "service_name": "...",
      "service_type": "...",
      "service_unit_price": 0.00,
      "has_subscription_date": true,
      "subscription_date_from": "...",
      "subscription_date_to": "...",
      "quantity": 1
    }
  ],
  "totalAmount": 0.00,
  "isChargeNow": false
}
```

### Statuses lifecycle
`new` → `used` (client pays via token link) | `expired` (token_expiry_date has passed — auto-updated on display)

### Feature flags (from `platformConfig.cmsAppFeatures`)
- `payment_request.value.allowed_service_types` — controls which Xero service types are available
- `payment_request.value.enable_charge_card_immediately` — enables the "charge card now" checkbox when company has a saved credit card

### Additional surfaces
- `src/views/admin/companies/edit/index.js` — legacy billing section (same flow)
- `src/views/admin/company-overview/billing.js` — alternative billing tab (same flow)
- `src/views/admin/sleek-workflow/workflow-task/tasks/agm-ar/eot-and-penalties/` — used to generate penalty payment requests from workflow tasks
