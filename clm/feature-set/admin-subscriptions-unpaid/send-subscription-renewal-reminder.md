# Send Subscription Renewal Reminder

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Send Subscription Renewal Reminder |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (internal Sleek billing operator) |
| **Business Outcome** | Prompt companies with non-auto subscriptions to renew before or after their due date, reducing revenue leakage from manual-renewal clients who miss their renewal window. |
| **Entry Point / Surface** | Admin Panel > Subscriptions > Unpaid (`/admin/subscriptions/unpaid/`) — Actions dropdown > "Resend Reminder" (visible only for non-auto subscriptions) |
| **Short Description** | From the Unpaid Subscriptions admin screen, an operator selects a non-auto subscription and triggers a payment reminder email via a dedicated API endpoint. The action is disabled for automatic-renewal subscriptions, which handle reminders differently. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Unpaid Subscriptions list view (same screen); subscription auto-renewal flow; Xero invoice lookup (`expected_external_payment_info.invoices`); Move to Paid action (same Actions menu); Cancel Subscription flow (same screen, auto-only) |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown (backend not in this repo; likely `companysubscriptions` or equivalent) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which email template is sent by the backend `/send-reminder` endpoint? Is there a rate limit or cooldown between reminders for the same subscription? Which markets use non-auto subscriptions (SG/HK/UK/AU)? DB collections touched by the backend are unknown from frontend code alone. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- Component: `src/views/admin/subscriptions/unpaid/index.js` — `AdminUnpaidSubscriptionsView`
- Layout: `AdminLayout` with `sidebarActiveMenuSubItemKey="unpaid-subscriptions"`
- "Resend Reminder" menu item rendered only when `!subscription.is_auto` (line 328–329)

### Reminder action (sendSubscriptionReminderEmail)
`src/views/admin/subscriptions/unpaid/index.js:264–278`

```js
sendSubscriptionReminderEmail = async (event, subscription) => {
  this.setState({ formIsLoading: true });
  const response = await api.sendSubscriptionReminderEmail(subscription._id)...
  // success: "Reminder has been sent successfully!"
}
```

### API call
`src/utils/api.js:1579–1582`

```js
function sendSubscriptionReminderEmail(companySubscriptionId, options = {}) {
  const endpoint = `${getBaseUrl()}/admin/company-subscriptions/${companySubscriptionId}/send-reminder`;
  return postResource(endpoint, options);
}
```

- Method: `POST`
- Route: `/admin/company-subscriptions/{companySubscriptionId}/send-reminder`
- Auth surface: admin-only route (AdminLayout + `/admin/` prefix)

### Subscription list query
`src/views/admin/subscriptions/unpaid/index.js:86–109`

`GET /admin/company-subscriptions` with params:
- `is_subscribed=true`, `is_cancelling=false`
- `sortBy=overdue_at`, `sortOrder=1`
- Optional filters: `overdue_at` (cutoff date), `company` (specific company), `is_auto`

Filter presets available to admin:
- `< 1 week (Non-auto)` — overdue_at ≤ +7 days
- `< 2 weeks (Non-auto)` — overdue_at ≤ +14 days
- `< 1 month (Non-auto)` — overdue_at ≤ +1 month
- `Automatic Renewals` — `is_auto=true`

### Xero integration
Subscription rows surface Xero invoice numbers and URLs from `expected_external_payment_info.invoices[0].{number,url}` (lines 287–288, 319–323), confirming invoices are tracked in Xero.

### Related actions on same screen
- **Move to Paid**: `PUT /admin/company-subscriptions/{id}/move-to-paid` (`api.moveSubscriptionToPaid`)
- **Cancel** (auto-only): `PUT /company-subscriptions/{id}/cancellation-request` (`api.cancelCompanySubscription`)
- **Manual Payment Info**: popover showing invoice number, tentative payment date, cheque number (from `expected_external_payment_info`)
