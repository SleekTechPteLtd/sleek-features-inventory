# Review Offboarding Requests

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Review Offboarding Requests |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables Operations teams to monitor, triage, and track all client offboarding requests across exit types and lifecycle stages, ensuring timely processing of client departures. |
| **Entry Point / Surface** | Sleek Billings Frontend > /offboarding-requests |
| **Short Description** | A paginated, filterable table listing all client offboarding requests. Users can filter by status (Pending, Approved, To Be Reviewed, Completed, Cancelled) via tabs and by request type (Partial Churn, Full Churn, Strike Off, Archive — each by Client or Sleek), search by company name, and sort by request date or last paid invoice date. Each row links to a detail view for full triage actions. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Offboarding Request Detail (`/offboarding-requests/:id`) — approve, reject, submit for review, complete, cancel actions; Admin App company overview (linked per row via `VITE_ADMIN_APP_URL`); Service Delivery API backend (`VITE_SERVICE_DELIVERY_API_URL`) |
| **Service / Repository** | sleek-billings-frontend; Service Delivery API (external backend) |
| **DB - Collections** | Unknown (backend service; not visible from frontend) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets/jurisdictions does this apply to? Is the Service Delivery API a separate microservice — what collections does it own? Can "System" requestor be further identified (automated rule or scheduler)? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/pages/Offboarding/OffboardingRequests.jsx`

- Main list page rendered at `/offboarding-requests`.
- **Status tabs** (line 449–478): Pending, Approved, To Be Reviewed, Completed, Cancelled, All Requests — mapped from `OFFBOARDING_REQUEST_STATUS` constants. Active tab drives the `statuses` filter sent to the API.
- **Request type multi-select filter** (line 308–374): options from `OFFBOARDING_REQUEST_TYPE` — 8 values covering partial churn, full churn, strike off, archive, each split by initiating party (Client vs Sleek).
- **Status multi-select filter** (line 376–444): visible only when "All Requests" tab is active.
- **Company name search** (line 295–306): debounced 500 ms (`SleekInputField`), queries `searchTerm` param.
- **Sortable columns** (line 23–26, 498–510): `requestDate` and `lastPaidInvoiceDate`, toggling ASC/DESC.
- **Columns displayed**: Company Name (links to admin app), Request Date, Last Paid Invoice Date, Status (badge), Request Type, Requested By (user name or "System" with tooltip "Automatically flagged for offboarding").
- **Pagination** (line 556–567): 20/50/100 per page via `TablePaginationFooter`.
- **State preservation** (line 258–277, 128–141): list filter/sort/page state is saved to router location state and restored when navigating back from the detail view.
- API call: `sleekServiceDeliveryApi.getOffboardingRequests(filters)` — params: `page`, `limit`, `sortBy`, `sortOrder`, `searchTerm`, `requestTypes[]`, `statuses[]`.

### `src/services/service-delivery-api.js` (lines 1093–1156)

- `GET /offboarding-requests` — list with query params (line 1093–1102).
- `GET /offboarding-requests/:id` — single request detail (line 1103–1111).
- `PUT /offboarding-requests/:id/approve` (line 1112–1119).
- `PUT /offboarding-requests/:id/reject` (line 1121–1128).
- `PUT /offboarding-requests/:id/submit-for-review` (line 1130–1137).
- `PUT /offboarding-requests/:id/complete` (line 1139–1146).
- `PUT /offboarding-requests/:id/cancel` (line 1148–1155).
- Base URL: `VITE_SERVICE_DELIVERY_API_URL` (line 3).

### `src/lib/constants.jsx` (lines 527–582)

- `OFFBOARDING_REQUEST_STATUS`: `pending`, `approved`, `to_be_reviewed`, `rejected`, `completed`, `cancelled`.
- `OFFBOARDING_REQUEST_TYPE`: `partial_churn_requested_by_client`, `partial_churn_requested_by_sleek`, `full_churn_requested_by_client`, `full_churn_requested_by_sleek`, `strike_off_requested_by_client`, `strike_off_requested_by_sleek`, `archive_requested_by_client`, `archive_requested_by_sleek`.
- `OFFBOARDING_REQUEST_STATUS_BADGE_VARIANT`: maps statuses to UI badge colors (default, success, primary, error).
