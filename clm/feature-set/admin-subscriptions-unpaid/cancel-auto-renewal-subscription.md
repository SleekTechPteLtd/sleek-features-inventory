# Cancel Auto-Renewal Subscription

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Cancel auto-renewal subscription |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Allows Sleek admins to halt a client's automatic billing cycle by submitting a cancellation request directly from the unpaid subscriptions dashboard, preventing unwanted future charges. |
| **Entry Point / Surface** | Sleek Admin > Subscriptions > Unpaid > Actions dropdown > Cancel (visible only for auto-renewal subscriptions) |
| **Short Description** | From the unpaid subscriptions list, an admin selects "Cancel" on an auto-renewing subscription row, confirms via a modal dialog, and the system submits a cancellation request via `PUT /company-subscriptions/:id/cancellation-request`. Non-auto subscriptions show "Delete" (disabled) instead of "Cancel". |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Unpaid subscriptions list view (`AdminUnpaidSubscriptionsView`), subscription auto-renewal system, backend cancellation-request processing, subscription status lifecycle |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown (frontend only; backend collection not inspected) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Does the backend immediately cancel the subscription or queue it for review/approval? Are there notifications sent to the client upon cancellation request? Does this interact with Xero invoice voiding? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Primary file
- `src/views/admin/subscriptions/unpaid/index.js` — `AdminUnpaidSubscriptionsView` React component

### Key methods
- `toggleDialog(event, subscription)` (line 391) — shows confirmation modal: "Are you sure you want to proceed with the cancellation request?"
- `handleCancelSubscription(event, subscription)` (line 414) — calls `api.cancelCompanySubscription(subscription._id)`, shows success toast "Request for cancellation of subscription has been submitted successfully!" on `response.ok`
- `renderBodyContent()` (line 280) — renders the Actions dropdown; "Cancel" MenuItem appears only when `subscription.is_auto === true`; non-auto subscriptions show a disabled "Delete" option instead

### API call
- `cancelCompanySubscription(companySubscriptionId)` in `src/utils/api.js` (line 1528)
- Endpoint: `PUT /company-subscriptions/${companySubscriptionId}/cancellation-request`

### Related API calls on same view
- `getAdminCompanySubscriptions` → `GET /admin/company-subscriptions` (fetches the list, filterable by `is_auto=true`)
- `moveSubscriptionToPaid` → `PUT /admin/company-subscriptions/:id/move-to-paid`
- `sendSubscriptionReminderEmail` → `POST /admin/company-subscriptions/:id/send-reminder` (non-auto only)

### UI behaviour
- The view uses colour-coded icons to distinguish auto-renewal vs. non-auto subscriptions by renewal urgency
- Filter options include "Automatic Renewals" (`is_auto=true`) to isolate auto-renewal subscriptions
- Xero invoice URL/number is shown per row but not directly manipulated by this action
