# Fetch and format consent list

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Fetch and format consent list |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Ensures each consent row only exposes role metadata that matches the CMS allowlist for add-employee flows, so filters and displays stay aligned with configured active role identifiers. |
| **Entry Point / Surface** | Sleek Admin > Auto-Sign Configuration — invoked from `AutoSignConfiguration` on mount, after CMS init, and when filters change (`fetchConsents` → `consentsFormatter`) |
| **Short Description** | Loads document-signing consents via `GET /admin/document-signing-consent` with query filters, limit, and offset. Re-reads CMS `add_employee_active_role_identifiers` and maps each consent’s `user.groups` to a `roles` array containing only groups whose `identifier` is in that allowlist; if the allowlist is empty, raw API rows are used unchanged. |
| **Variants / Markets** | Unknown (CMS-driven; not enumerated in this code path) |
| **Dependencies / Related Flows** | `getCmsConfig` / `getPlatformConfig` + `getAppFeatureProp` for `incorp_transfer_workflow` → `auto_sign_documents.value.add_employee_active_role_identifiers`; upstream API backing `/admin/document-signing-consent`; consumer: `DataTable` and filters in the same module |
| **Service / Repository** | `sleek-website` — `src/views/admin/auto-sign-configuration/index.js`; `src/utils/api.js` |
| **DB - Collections** | Unknown (consents served by API; not defined in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/auto-sign-configuration/index.js`

- **Fetch:** `fetchConsents` builds `requestParams` with `getDefaultFilter()` (URL query: `userId`, `roleId`, `automatedSignature`, split to arrays where needed), `limit`, `offset`, then `api.getAllConsents(requestParams)` (lines 94–113).
- **Format:** `consentsFormatter` calls `getCmsConfig()` again, returns early with unmodified `data` if config missing or `add_employee_active_role_identifiers` is empty (lines 170–176). Otherwise maps each consent: `formattedRoles = consent.user.groups.filter(({ identifier }) => identifier && addEmployeeActiveRoleIdentifiersValue.includes(identifier))`, spreads `{ ...consent, roles: formattedRoles }` (lines 178–184).
- **Call sites:** Initial load and `handleFilterChange` / `updateDocumentSigningConsent` success paths call `fetchConsents()` (lines 66–70, 364, 387, 403).

### `src/utils/api.js`

- `getAllConsents(options)`: `GET ${getBaseUrl()}/admin/document-signing-consent` via `getResource` (lines 2077–2079).
