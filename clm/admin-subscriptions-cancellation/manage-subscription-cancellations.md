# Manage Subscription Cancellations

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Subscription Cancellations |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Enables ops/admin staff to track and action every subscription flagged for cancellation, ensuring no cancellation request falls through the cracks and each one is formally closed out. |
| **Entry Point / Surface** | Sleek Admin > Subscriptions > Cancellation |
| **Short Description** | Admins view a paginated list of subscriptions where `is_cancelling=true`, filter by company and cancellation status, and manually advance each subscription through a three-stage workflow: New Cancellation → Cancellation in Process → Cancellation Complete. Each status transition is confirmed via a modal. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: customer-initiated cancellation request (`PUT /company-subscriptions/:id/cancellation-request`) sets `is_cancelling=true`; Downstream: once marked `done`, the subscription record reflects the completed cancellation date; Related: Admin Subscriptions list views (admin-subscriptions-new, admin-subscriptions-unpaid) |
| **Service / Repository** | sleek-website (frontend); backend API at `/admin/company-subscriptions` (separate service) |
| **DB - Collections** | Unknown — backend API owns persistence; frontend surfaces `companySubscriptions` array with fields: `_id`, `company._id`, `company.name`, `service`, `duration`, `cancellation_status`, `overdue_at`, `updatedAt`, `owner.first_name`, `owner.phone`, `owner.email` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which backend service owns `/admin/company-subscriptions`? What triggers `is_cancelling=true` (customer portal, ops tool, or both)? Are there SLA or overdue rules tied to `overdue_at`? Are markets scoped (SG/HK/UK/AU all use this workflow)? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/views/admin/subscriptions/cancellation/index.js` — `AdminCancelledSubscriptionsView` root component; fetches subscriptions with `is_cancelling=true`, manages filter state (`cancellation_status`, `selectedCompanyId`), handles status update via `handleUpdateCancellationStatus`, and renders confirmation dialog before committing transitions.
- `src/views/admin/subscriptions/cancellation/table-row.js` — `TableRow` renders one subscription row: company name (linked to `/dashboard/?cid=`), service, duration in months, completion date (shown only when `status=done`), and owner contact details (name, phone, email).
- `src/views/admin/subscriptions/cancellation/cancellation-dropdown.js` — `CancellationDropdown` renders a BlueprintJS `Popover` menu; suppresses the option matching the current status so only valid forward/backward transitions are offered.

### API calls
| Call | Endpoint | Method | Purpose |
|---|---|---|---|
| `getAdminCompanySubscriptions` | `GET /admin/company-subscriptions?is_cancelling=true&sortBy=overdue_at&...` | GET | Fetch paginated list, filtered by `cancellation_status` and `company` |
| `updateSubscriptionCancellationStatus` | `PUT /admin/company-subscriptions/:id` | PUT | Advance or revert a subscription's `cancellation_status` |

### Cancellation workflow states
| `cancellation_status` | Label shown |
|---|---|
| `new` | New Cancellation |
| `pending` | Cancellation in Process |
| `done` | Cancellation Complete |

### Shared utilities
- `src/views/admin/subscriptions/common.js` — shared pagination (`handleChangePage`, `handleClickPrevPage/NextPage`) and company-search helpers (`handleSelectCompany`, `handleSearchCompany`, `fetchCompaniesList`) reused across admin subscription views.
- `src/utils/api.js:1474` — `getAdminCompanySubscriptions`
- `src/utils/api.js:1533` — `updateSubscriptionCancellationStatus`
