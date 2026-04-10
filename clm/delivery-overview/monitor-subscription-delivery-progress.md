# Monitor Subscription Delivery Progress

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Monitor Subscription Delivery Progress |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations Staff / Delivery Team |
| **Business Outcome** | Gives delivery team staff real-time visibility into task completion rates and overdue work across all client subscriptions, enabling proactive intervention before SLA breaches. |
| **Entry Point / Surface** | Sleek App > Delivery > Subscription Progress (`/delivery/overview`) |
| **Short Description** | Staff view a paginated list of all client subscriptions with task completion %, overdue task counts, delivery status, and priority labels. Clicking a row opens a detail panel with an overall progress bar, per-deliverable breakdown, and expandable task-level status. Status banners alert staff to deactivated, discontinued, or upgraded/downgraded subscriptions. |
| **Variants / Markets** | Unknown — priority labels include SG-specific options (AGM Due Soon, etc.); broader market split not determinable from frontend code |
| **Dependencies / Related Flows** | Delivery Task Tracker (`/delivery/tasks` — linked via "View all tasks" button); Sleek Billings API (`getCustomerSubscriptionsByCompanyId` — used to navigate to successor subscription on upgrade/downgrade); Admin App (company overview deep-link from company name column); Subscription renewal/upgrade flow (renewalStatus drives SubscriptionStatusAlert banners) |
| **Service / Repository** | sleek-billings-frontend; sleek-service-delivery-api (backend, `VITE_SERVICE_DELIVERY_API_URL`) |
| **DB - Collections** | Unknown — all persistence is in the backend service; subscriptions, deliverables, tasks, and users collections implied by API shape |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets (SG/HK/UK/AU) use this feature? What are the specific staff role types that have access (bookkeeper vs. manager vs. all)? What backend service/repo serves VITE_SERVICE_DELIVERY_API_URL and what DB collections does it own? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `pages/Delivery/DeliveryOverview.jsx` — page component; page title "Subscription Progress" (line 837); route `/delivery/overview` (confirmed by SubscriptionStatusAlert navigation on line 78)

### List view
- Two tabs: "All Subscriptions" / "Assigned to Me" (line 842–848); `assignedToMe` URL param controls default tab
- Search box: debounced 500 ms, propagated to API as `search` query param (lines 223–231)
- Filter drawer (lines 68–82, 639–798): filter by Labels, Service FYE year, Company Assignee, Delivery Status
- URL params preserve search/filter state for shareable links (line 30, 38)
- Columns: Company Name (link to Admin App), Subscription name, Priority Labels (inline editable), Subscription Period + FYE, Tasks Overdue, Last Completed Task (lines 407–528)
- Sort: company name, subscriptionPeriod, overdueTasksCount (server-side, lines 289–301)
- Pagination: server-side, default 20/page; options 20/50/100 (lines 1007–1018)

### Task metrics (computed client-side from nested data)
- `getTasksCounts()` (lines 89–128): calculates total, done, not-required, overdue (past dueDate, excluding DONE/NOT_REQUIRED), and completionPercentage = (done + notRequired) / total × 100
- Overdue badge turns red when count > 0 (line 1144)
- Completion badge: green at 100%, blue ≥75%, yellow ≥50%, orange >0%, gray at 0% (lines 304–316)

### Detail panel (lines 1021–1193)
- Opens on row click; shows delivery status, labels, subscription ref#, start/end date, service FYE, last completed task
- Overall progress bar (`taskSummary.completionPercentage`)
- Deliverable breakdown table: per-deliverable overdue count and completed/total tasks; expandable to show individual tasks with `StatusBadge` (DONE / NOT_REQUIRED / TO_DO)
- "View all tasks" opens `/delivery/tasks?search=<company>&subscriptionRefNumber=<ref>` in new tab (lines 1106–1120)

### Subscription status alerts (`components/SubscriptionStatusAlert.jsx`)
- `deactivated` → yellow warning banner ("Deactivated due to billing changes")
- `discontinued` + `upgraded`/`downgraded` renewalStatus → blue info banner with "View new subscription" link (calls `sleekBillingsApi.getCustomerSubscriptionsByCompanyId`, finds successor by `existingSubscription` field, opens new tab)
- `discontinued` (plain) → gray info banner ("Review if any remaining work is required")

### Delivery status values (`src/lib/constants.jsx`, lines 349–413)
`active`, `delivered`, `discontinued`, `inactive`, `none`, `toBeStarted`, `toOffboard`, `deactivated`

### API surface (`services/service-delivery-api.js`)
- Base URL: `VITE_SERVICE_DELIVERY_API_URL`
- Auth: `Authorization: Bearer <jwt>` or legacy token; `App-Origin: admin | admin-sso`
- Key calls used by this feature:
  - `GET /subscriptions` — paginated list with `page`, `limit`, `sortBy`, `sortOrder`, `assignedUserId`, `search`, `priorityLabels`, `serviceFyeYears`, `companyAssigneeIds`, `deliveryStatuses` (lines 54–68)
  - `PATCH /subscriptions/:id` — inline label updates (line 360)
  - `GET /users` — populates company-assignee filter (lines 532–545)
- Response envelope: `{ success, message, data, timestamp }` unwrapped by `unwrapServiceDeliveryPayload()` (lines 40–50)
