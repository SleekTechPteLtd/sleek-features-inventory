# Filter and Search Delivery Tasks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Filter and Search Delivery Tasks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators can narrow a cross-company task backlog to only the tasks requiring their attention, reducing noise and enabling focused execution across their service delivery portfolio. |
| **Entry Point / Surface** | Sleek App > Delivery Tasks (`/delivery/tasks`) — filter drawer, keyword search bar, and quick-filter chips in `TasksDashboard` |
| **Short Description** | Provides a multi-dimensional filter panel and debounced keyword search on the Delivery Tasks dashboard. Operators can filter tasks by assignee (specific user, "assigned", or "unassigned"), assignee role type, client company (assigned-to-me or all), subscription priority label, subscription delivery status, service financial year end (7-year sliding window), task template name, task status, and subscription reference number. All filter changes trigger a server-side `POST /tasks/search` call with abort-controller cancellation for stale in-flight requests. |
| **Variants / Markets** | Unknown — priority label options are platform-dependent (`billingConfig.platform`), but no explicit market branching is visible in the filter logic |
| **Dependencies / Related Flows** | `sleekServiceDeliveryApi.searchTasks` (POST /tasks/search); `sleekServiceDeliveryApi.getAllUsers`; `sleekServiceDeliveryApi.getAllCompanies`; `sleekServiceDeliveryApi.getDeliverableTemplatesList`; `sleekBillingsApi.getCustomerSubscriptionsByCompanyId` (used in result rows for upgraded/downgraded subscription navigation); `TasksList` (renders paginated, sortable results); Delivery Overview (`/delivery/overview`); Task Assignments (`/delivery/task-assignments`) |
| **Service / Repository** | sleek-billings-frontend; sleek-service-delivery (backend — hosts `/tasks/search` endpoint) |
| **DB - Collections** | Unknown — filter parameters are resolved server-side; no MongoDB collections are directly referenced in frontend code |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets/platforms have priority label options configured in `billingConfig`? Are all filter dimensions supported server-side for all markets, or do some require backend feature flags? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/pages/DeliveryTasks/TasksDashboard.jsx` — filter state management, filter drawer UI, chip quick-filters, keyword search, subscription ref search, debounced user/company/task-template search; calls `getAllUsers`, `getAllCompanies`, `getDeliverableTemplatesList` on mount
- `src/pages/DeliveryTasks/TasksList.jsx` — consumes `filters`, `searchTerm`, `subscriptionRefNumber` props; calls `sleekServiceDeliveryApi.searchTasks(...)` on every filter/sort/page change with AbortController cancellation

### Filter dimensions sent to `POST /tasks/search`
| Parameter | Source filter |
|---|---|
| `assignedUserIds` | `filterByUsers` (excludes "unassigned"/"assigned" sentinel values) |
| `filterByUnassigned` | `filterByUsers.includes("unassigned")` |
| `filterByAssigned` | `filterByUsers.includes("assigned")` |
| `assignedRoleTypes` | `filterByRoles` |
| `companyIds` | `filterByCompanies` |
| `subscriptionLabels` | `filterByLabels` (priority labels) |
| `subscriptionDeliveryStatuses` | `filterByDeliveryStatuses` (toBeStarted, active, toOffboard, discontinued, deactivated) |
| `serviceFyeYears` | `filterByServiceFYEs` (string years, 7-year window) |
| `filterMilestoneTasks` | boolean toggle |
| `taskTemplateIds` | `filterByTaskTemplateIds` |
| `taskStatuses` | `filterByTaskStatuses` (TO_DO, DONE, NOT_REQUIRED) |
| `searchTerm` | free-text keyword search |
| `filterBySubscriptionRefNumber` | subscription reference number input |
| `taskDueStatus` | active tab: OVERDUE / DUE_SOON / NOT_DUE / COMPLETED / ALL |

### API call
- `sleekServiceDeliveryApi.searchTasks` → `serviceDeliveryApi.post("/tasks/search", params, config)` — `src/services/service-delivery-api.js:565`

### Default filter state on load
- `filterByUsers`: logged-in user's ID (unless navigating from a search URL)
- `filterByDeliveryStatuses`: `["toBeStarted", "active"]`
- `filterByServiceFYEs`: `[currentYear - 1, currentYear]`

### Sort & pagination
- Sortable columns: `companyName`, `dueDate`, `completedDate`, `subscriptionPeriod`, `financialYearEnd`
- Default sort: `dueDate ASC` (non-completed tabs), `completedDate DESC` (Completed tab)
- Pagination: configurable page size via `TablePaginationFooter`
