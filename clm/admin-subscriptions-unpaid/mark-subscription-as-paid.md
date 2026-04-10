# Mark Subscription as Paid

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Mark subscription as paid |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Allows operations staff to close out offline payment cycles by manually flipping a subscription from unpaid to paid after confirming bank transfer or cheque receipt, keeping subscription status accurate without requiring an online payment gateway transaction. |
| **Entry Point / Surface** | Sleek Admin > Subscriptions > Unpaid > Actions > Move to Paid |
| **Short Description** | Admin views a paginated list of unpaid company subscriptions, inspects any pre-recorded offline payment info (bank transfer, cheque), and clicks "Move to Paid" to mark the subscription paid. The list refreshes immediately on success. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Unpaid subscriptions list (same screen); Xero invoice creation (invoice numbers and URLs surfaced per subscription); offline/external payment recording flow (populates `expected_external_payment_info`); subscription reminder email dispatch; auto-renewal cancellation flow (also on this screen) |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown (company_subscriptions inferred; not readable from frontend code) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | What backend validation runs before marking paid (API returns 422 on failure — specific conditions unknown)? Does marking paid trigger any downstream event (Xero sync, email notification, Kafka event)? Which markets use this flow vs. auto-renewal? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Primary file
- `src/views/admin/subscriptions/unpaid/index.js` — `AdminUnpaidSubscriptionsView` React component

### Key method
- `changeUnpaidSubscriptionToPaid(event, subscriptionId)` (line 76) — calls `api.moveSubscriptionToPaid(subscriptionId)`, handles 422 error with toast, refreshes list on success.

### API calls (from `src/utils/api.js`)
| Function | Method | Endpoint |
|---|---|---|
| `moveSubscriptionToPaid` (line 1561) | `PUT` | `/admin/company-subscriptions/{id}/move-to-paid` |
| `getAdminCompanySubscriptions` (line 1474) | `GET` | `/admin/company-subscriptions` |
| `sendSubscriptionReminderEmail` (line 1579) | `POST` | `/admin/company-subscriptions/{id}/send-reminder` |
| `cancelCompanySubscription` (line 1528) | `PUT` | `/company-subscriptions/{id}/cancellation-request` |

### Supporting component
- `src/views/admin/subscriptions/unpaid/manual-payment-info.js` — `ManualPaymentInfo` popover: shows Invoice Number (Xero URL), Tentative Payment Date (`expected_pay_at`), Cheque Number. Rendered per row when `expected_external_payment_info` is non-null.

### List query parameters
`is_subscribed=true`, `is_cancelling=false`, `sortBy=overdue_at`, `sortOrder=1`, paginated 20/page. Filterable by overdue window (1 week / 2 weeks / 1 month / auto-renewal) and by company name.

### Overdue colour coding
Five visual states driven by `subscription.overdue_at` vs. current date: automatic renewal, 1 month, 2 weeks, 1 week, overdue. Rendered via `renderEmojiForRenewalDate()` (line 366).

### External integrations observed
- **Xero** — invoice number and URL exposed via `expected_external_payment_info.invoices[0]` (line 287–288). Direct deep-link to Xero invoice rendered in the table.
- **Offline payments** — `expected_external_payment_info` field records bank transfer / cheque details upstream of this screen; this screen is the confirmation + status-flip step.
