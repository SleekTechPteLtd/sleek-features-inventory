# Advance request workflow status

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Advance request workflow status |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin / Operations |
| **Business Outcome** | Internal operators can move a client document request through its lifecycle, record why, and optionally alert the company owner when the status changes so expectations stay aligned. |
| **Entry Point / Surface** | Sleek Admin > Requests > open a request (`AdminEditRequestView`, query `?cid=` company id, `?rid=` request id; breadcrumbs Requests → request id; `sidebarActiveMenuItemKey="requests"`) — **Request Status** card |
| **Short Description** | Staff set **Status** from a fixed list, enter **Remarks**, and toggle **Notify the company** so the owner may receive a notification. Submit opens a confirmation dialog (copy reflects whether notification is on), then persists via the change-status API. Status and remarks are loaded with the request instance when the page opens. |
| **Variants / Markets** | Unknown (status labels include SG-oriented values such as “Referred to ACRA” in shared constants; tenant not fixed in this view) |
| **Dependencies / Related Flows** | Loads request context with `getCompanyRequestInstance`; downstream email or in-app notification is handled by the main API when `send_notification` is true. Related: **Update Request** on the same page (`editRequestInstance`) updates document fields separately from status. |
| **Service / Repository** | `sleek-website`: `src/views/admin/requests/edit.js`, `src/utils/api.js` (`changeRequestInstanceStatus`, `getCompanyRequestInstance`). Main API (`getBaseUrl()`). |
| **DB - Collections** | Unknown (request instance `status` / `status_remarks` persisted by backend) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact notification channel and templates when `send_notification` is true; admin auth rules on `POST /admin/request-instances/:id/change-status`. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/requests/edit.js`

- **Request Status UI:** `renderRequestStatusForm()` — “Request Status” card with required `select` `request_status`, `textarea` `request_status_remarks`, checkbox `change-status-notify-user` (“Notify the company”), helper text that notification is optional; submit **Update Status** (`requestStatusFormHandleSubmit`) (lines 1077–1138).
- **Initial values:** `getRequestInstance` maps `requestInstance.status` → `formValues.request_status`, `requestInstance.status_remarks` → `formValues.request_status_remarks` (lines 1302–1304).
- **Submit flow:** `requestStatusFormHandleSubmit` prevents default, opens confirm dialog (`dialogPrimaryButtonText` “Update” vs “Update and Notify”); body text states whether the **company owner** will be notified (lines 1381–1423). On confirm → `changeRequestStatus()` with `requestStatusFormIsLoading`, calls `api.changeRequestInstanceStatus(this.state.requestId, { admin: true, body: JSON.stringify({ status, status_remarks, send_notification }) })` where `send_notification` maps from `formValues["change-status-notify-user"]` (lines 1383–1390). Success: alert “Request status has been updated successfully!” (lines 1391–1399). Error: `getRequestInstance()` refresh + `viewUtil.showResponseErrorAlert` (lines 1400–1404).
- **Status options:** `renderRequestStatusSelectOptions` uses `REQUEST_STATUSES` from `constants` (lines 1217–1222, import line 13).

### `src/utils/constants.js`

- **`REQUEST_STATUSES`:** Values include `processing_by_sleek`, `waiting_for_signatures`, `voided`, `referred_to_acra`, `success`, `fail` (labels: Processing by Sleek, Pending Signatures, Document Voided, Referred to ACRA, Success, Cancelled) (lines 1324–1331).

### `src/utils/api.js`

- **`changeRequestInstanceStatus`:** `POST `${getBaseUrl()}/request-instances/${requestInstanceId}/change-status`` via `postResource`; with `options.admin === true`, `postResource` rewrites to **`POST ${getBaseUrl()}/admin/request-instances/${requestInstanceId}/change-status`** (lines 1210–1212; `postResource` admin prefix lines 147–150).
