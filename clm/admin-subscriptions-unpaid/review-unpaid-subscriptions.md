# Review Unpaid Subscriptions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Review Unpaid Subscriptions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Enables admins to monitor all company subscriptions awaiting payment, triaged by overdue urgency and renewal type, so they can prioritise payment follow-up and minimise revenue leakage. |
| **Entry Point / Surface** | Sleek Admin App > Subscriptions > Unpaid (`/admin/subscriptions/unpaid/`) |
| **Short Description** | Paginated admin dashboard listing active non-cancelling company subscriptions with unpaid status, filtered by overdue urgency window (< 1 week / < 2 weeks / < 1 month, non-auto) or renewal type (automatic), with colour-coded urgency icons, Xero invoice links, manual payment info, and quick actions to resend reminders, mark as paid, or initiate cancellation. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Xero (invoice URL display); email/notification system (subscription reminder); payment pipeline (move-to-paid transition); company search API; cancellation request flow |
| **Service / Repository** | sleek-website |
| **DB - Collections** | company_subscriptions, companies (inferred from API query params and response shapes) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets use this view (SG/HK/UK/AU)? No market-specific branching found in code. Is "Create Invoice" action intentionally disabled or pending implementation? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/views/admin/subscriptions/unpaid/index.js` — `AdminUnpaidSubscriptionsView` React component; main list view, filter logic, action handlers
- `src/views/admin/subscriptions/unpaid/manual-payment-info.js` — `ManualPaymentInfo` popover component; surfaces invoice number, tentative payment date, cheque number, Xero URL for bank-transfer/other payments
- `src/views/admin/subscriptions/common.js` — shared pagination helpers (`handleChangePage`, `handleClickPrevPage`, `handleClickNextPage`), company search/select (`fetchCompaniesList`, `handleSelectCompany`, `handleSelectNoCompany`, `handleSearchCompany`), and `getUser` auth check

### Filters
Dropdown in toolbar drives `overdue_at` and `is_auto` query params:
- `filter-by-1-week` → `overdue_at = now + 1 week`, non-auto
- `filter-by-2-weeks` → `overdue_at = now + 2 weeks`, non-auto
- `filter-by-1-month` → `overdue_at = now + 1 month`, non-auto
- `is-auto` → `is_auto = true` (automatic renewals)

Company filter: admin can search and select a specific company via a typeahead Select.

Pagination: 20 per page, sorted by `overdue_at` ascending.

### API endpoints (via `src/utils/api.js`)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/admin/company-subscriptions` | List unpaid subscriptions; query params: `is_subscribed=true`, `is_cancelling=false`, `sortBy=overdue_at`, `sortOrder=1`, `skip`, `overdue_at`, `company`, `is_auto` |
| PUT | `/admin/company-subscriptions/:id/move-to-paid` | Mark subscription as paid (`moveSubscriptionToPaid`) |
| POST | `/admin/company-subscriptions/:id/send-reminder` | Send payment reminder email (`sendSubscriptionReminderEmail`) |
| PUT | `/company-subscriptions/:id/cancellation-request` | Initiate cancellation request for auto-renewal subscriptions (`cancelCompanySubscription`) |

### Urgency colour codes (rendered via `renderEmojiForRenewalDate`)
| Icon | Condition |
|---|---|
| `automatic_renewal.svg` | `subscription.is_auto === true` |
| `1month.svg` | `overdue_at > now + 14 days` (non-auto) |
| `2weeks.svg` | `now + 7 days < overdue_at ≤ now + 14 days` (non-auto) |
| `1week.svg` | `now ≤ overdue_at ≤ now + 7 days` (non-auto) |
| `overdue.svg` | `overdue_at < now` (non-auto) |

### Row actions
- **Resend Reminder** — non-auto subscriptions only; triggers `POST /admin/company-subscriptions/:id/send-reminder`
- **Cancel** — auto-renewal subscriptions only; confirmation dialog then `PUT /company-subscriptions/:id/cancellation-request`
- **Delete** — disabled (non-auto)
- **Create Invoice** — disabled (all)
- **Move to Paid** — all subscriptions; triggers `PUT /admin/company-subscriptions/:id/move-to-paid`

### External system surface
- **Xero**: Invoice number and URL displayed in both the main table column and the `ManualPaymentInfo` popover; sourced from `subscription.expected_external_payment_info.invoices[0]`
