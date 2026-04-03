# Submit Nium RFI questionnaires

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Submit Nium RFI questionnaires |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations user (Sleek Admin, business-account permission) |
| **Business Outcome** | Pending Nium business-account requests for information (RFIs) move forward after operators capture and submit the required answers in the schema-driven form. |
| **Entry Point / Surface** | Sleek Admin > RFI (sidebar) → list at `/admin/rfi/` → **RFI detail** at `/admin/rfi/detail/?id={rfiId}` (opened from the table “Open” action). |
| **Short Description** | Loads one RFI by id from the SBA API Gateway. When status is `requested`, renders Nium’s JSON Schema (`rfi.request`) with React JSON Schema Form (AJV8), optional answers (`rfi.response`), and a hidden-widget UI schema for read-only fields. Submit sends the form payload via PATCH as `response` body; success toasts and redirects to the RFI list. Status, labels, and guidance copy reflect Nium lifecycle (requested → submitted → approved/rejected/expired). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **SBA API Gateway** (`getBaseUrl()` → `/api/v1/rfi`, `/api/v1/rfi/:id`); **Nium** as the RFI issuer (schema and status semantics); **company shareholders** via `getCompanyShareholders(companyId)` for contextual “company admin contact” on the detail page; RFI list/browse (`rfi-table.js` → detail link). |
| **Service / Repository** | sleek-website (admin UI); SBA API Gateway / downstream services (not in this repo) |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact backend persistence (MongoDB collection names, Nium callback timing) is not visible from the website bundle; market-specific RFI rules if any. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Webpack entry**: `admin/rfi/detail` → `src/views/admin/rfi/detail/index.js` (paired HTML under `pages/admin/rfi/detail/` per webpack config).
- **Auth gate**: `getUser` in `src/views/admin/rfi/common.js` — requires verified email and `permissions.business_account` in `EDIT`, `FULL`, or `READ` (`BUSINESS_ACCOUNT_PERMISSION`); otherwise redirect to `/admin` or `/verify/`.
- **Status model**: `RFIStatus` in `common.js` — `requested`, `submitted`, `approved`, `rejected`, `expired`. `rfi-status.js` maps these to operator-facing labels/descriptions (e.g. “REQUESTED BY NIUM”, “Processing by NIUM”).
- **Load RFI**: `api.getRFI(rfiId)` — `GET ${getBaseUrl()}/api/v1/rfi/${rfiId}` in `src/utils/api-gateway.js` (`getRFI`). Query param `id` from `window.location.search` (`detail/index.js`).
- **Form rendering**: `@rjsf/core` + `@rjsf/validator-ajv8` — `schema={rfi.request}`, `formData={rfi.response}`, form read-only when status is not `requested` or while submitting. `buildUISchema(rfi)` hides widgets for properties marked `readOnly` under each template key in `request.properties`.
- **Submit**: `api.submitRFI(rfiId, formData)` — `PATCH ${getBaseUrl()}/api/v1/rfi/${rfiId}` with `body: JSON.stringify({ response: rfiData })` (`submitRFI` in `api-gateway.js`). Surfaces `data.errors[0].message` on failure; success uses `BottomRightToaster` then `window.location = '/admin/rfi'` after 1s.
- **Gateway base URL**: `getBaseUrl()` — `SBA_API_GATEWAY_URL` env, else production `https://sg-backend.sleek.com/sbaapigateway`, else dev `http://localhost:4315`.
- **Contact panel**: `getCompanyShareholders(companyId)` from `src/utils/api` when `rfi.companyId` is set — display only, not part of submit payload in this view.
- **Layout**: `AdminLayout` with `sidebarActiveMenuItemKey="rfi"`, `hideDrawer={true}`.
