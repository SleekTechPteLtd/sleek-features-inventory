# Complete Nium RFI questionnaire

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Complete Nium RFI questionnaire |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin / Operations (Sleek staff with business account read-or-better permission) |
| **Business Outcome** | Staff can supply Nium-requested information on behalf of a company so the Nium RFI can move forward after review and submission. |
| **Entry Point / Surface** | Sleek Admin > **RFI** (`sidebarActiveMenuItemKey="rfi"`) > open a row or navigate to detail — `admin/rfi/detail` with query `?id=` RFI id (`RFIDetail`, `rfiId` from `querystring.parse`) |
| **Short Description** | The detail page loads one RFI from the SBA API Gateway, shows Nium workflow status and guidance copy, renders the dynamic JSON Schema questionnaire (RJSF) when a schema is present, and shows the company owner’s contact (name, email, phone) for coordination. When status is **requested**, staff edit and submit answers; submission PATCHes the response payload and returns to the RFI list on success. Read-only fields in the schema are hidden in the UI when filling is allowed. |
| **Variants / Markets** | Unknown (Nium-facing; no market slug in this view) |
| **Dependencies / Related Flows** | **Upstream:** RFI list (`admin/rfi/index.js`) uses `getRFIs` to discover RFIs. **APIs:** SBA API Gateway `GET`/`PATCH` `/api/v1/rfi/:id`; main Sleek API `getCompanyShareholders` → `GET .../companies/:companyId/company-users` to resolve the owner contact. **Downstream:** Nium processes submission after PATCH (backend). |
| **Service / Repository** | `sleek-website`: `src/views/admin/rfi/detail/index.js`, `src/views/admin/rfi/common.js`, `src/views/admin/rfi/components/rfi-status.js`, `src/utils/api-gateway.js`, `src/utils/api.js` (`getCompanyShareholders`). **SBA API Gateway** (`getBaseUrl()` in `api-gateway.js`). |
| **DB - Collections** | Unknown (RFI record and responses persisted by SBA / gateway backend) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact admin auth model on gateway routes beyond session/`getDefaultHeaders()`; error shape for failed PATCH beyond `data.errors.0.message`; whether `getCompanyShareholders` naming still matches “all company users” used to find `is_owner`. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/rfi/common.js`

- **`RFIStatus`:** `requested`, `submitted`, `approved`, `rejected`, `expired` (lines 6–12).
- **`getUser`:** Loads current user via main `api.getUser()`; requires verified email (`registered_at`) and `permissions.business_account` in `EDIT` \| `FULL` \| `READ` (`BUSINESS_ACCOUNT_PERMISSION`); otherwise redirects to `/verify/` or `/admin` (lines 14–29).

### `src/views/admin/rfi/components/rfi-status.js`

- **Status labels:** Maps statuses to user-facing strings such as “REQUESTED BY NIUM”, “SUBMITTED”, “APPROVED BY NIUM”, “REJECTED BY NIUM”, “EXPIRED” (lines 4–10).
- **Guidance:** e.g. requested → “Please contact client for the requested information”; submitted → “Submitted. Processing by NIUM” (lines 12–18).

### `src/views/admin/rfi/detail/index.js`

- **Load:** `api.getRFI(rfiId)`; then `getCompanyShareholders(foundRFI.companyId)` and sets owner via `companyUsers.find((companyUser) => companyUser.is_owner)` (lines 32–48, 126–144).
- **Form:** `@rjsf/core` `Form` with `schema={rfi.request}`, `formData={rfi.response}`, `validator` from `@rjsf/validator-ajv8`; `readonly` when `rfi.status !== RFIStatus.REQUESTED || isSubmitting` (lines 97–104).
- **Submit:** `api.submitRFI(rfiId, formData)`; surfaces `get(result, "data.errors.0.message")` via `TopToaster`; success uses `BottomRightToaster` and redirects to `/admin/rfi` (lines 56–75, 158–159).
- **`buildUISchema`:** For `REQUESTED`, walks `request.properties` and sets `"ui:widget": "hidden"` for nested properties marked `readOnly` in the schema (lines 169–191).

### `src/utils/api-gateway.js`

- **Base URL:** `SBA_API_GATEWAY_URL` or prod `https://sg-backend.sleek.com/sbaapigateway` / dev `http://localhost:4315` (lines 6–14).
- **`getRFI`:** `GET ${getBaseUrl()}/api/v1/rfi/${rfiId}` via `getResource` (lines 79–81).
- **`submitRFI`:** `PATCH` same path with `body: JSON.stringify({response: rfiData})` via `patchResource` (lines 84–86).

### `src/utils/api.js` (supporting)

- **`getCompanyShareholders`:** `GET ${getBaseUrl()}/companies/${companyId}/company-users` (lines 475–476) — detail page uses returned `data` to locate the owner.
