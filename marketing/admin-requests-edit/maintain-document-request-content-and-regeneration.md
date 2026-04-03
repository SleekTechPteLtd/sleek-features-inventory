# Maintain document request content and regeneration

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Maintain document request content and regeneration |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Internal operators can align a client’s document request with the right corporate parties, template variables, and optional custom uploads, then refresh auto-generated HTML/PDF output so signed legal documents match current company data. |
| **Entry Point / Surface** | Sleek Admin > Requests > **Edit Request** (`AdminEditRequestView`, `sidebarActiveMenuItemKey="requests"`; breadcrumbs to `/admin/requests/`; page loaded with `?cid=` and `?rid=` query params) |
| **Short Description** | Operators review request metadata (company, template name, submission date, PandaDoc link, signed file). They may toggle **Use custom document** and upload a client file (PDF/JPG/PNG via company file storage), or edit **Document name** and template-bound **Document Data**: directors, shareholders, corp sec, share class/transaction, retiring directors, chairman, and CMS-driven custom variables (`document_fields`, date pickers). When **auto-populate** is enabled for the template, they use **Regenerate Request** (`autoPopulateRequestInstance`) or constrained **Update Request** flows; otherwise **Update Request** persists edits via `editRequestInstance`. A rich **Document Editor** supports manual HTML overrides, PDF export, and sending to SleekSign/PandaDoc. **Request Status** is updated separately with optional company notification. |
| **Variants / Markets** | Unknown (UI branches on CMS `request_templates`, `incorp_transfer_workflow`, and HK-specific automated templates such as share certificates; not hard-coded to a single market in this view) |
| **Dependencies / Related Flows** | Request instance load (`GET /companies/:companyId/request-instances/:id`); admin update (`PUT /admin/request-instances/:id`); auto-populate (`POST /admin/companies/:companyId/request-instances/:id/auto-populate`); status change (`POST /request-instances/:id/change-status`); company users (`GET /companies/:id/company-users` for directors/shareholders); corp sec directory (`GET /admin/users/admins` with group filter); HTML→PDF and e-sign (`POST /document-templates/convert-html-to-pdf`, `POST /request-instances/:id/send-for-signature`, legacy PandaDoc route); files service uploads/downloads; SleekSign iframe login. Downstream: customer signing and PandaDoc/SleekSign workflows. |
| **Service / Repository** | `sleek-website`: `src/views/admin/requests/edit.js`, `src/utils/api.js` (`getCompanyRequestInstance`, `editRequestInstance`, `autoPopulateRequestInstance`, `changeRequestInstanceStatus`, `getCompany`, `getCompanyDirectors`, `getCompanyShareholders`, `getAdminsByGroup`, `getCompanyRegistrableControllers`, `convertHtmlToPdf`, `sendRequestInstanceForSignature`, `sendRequestInstanceForSignaturePandadoc`, `getFileBaseUrl`, `moveFile`, `getFiles`). Main API and Files microservice (config-driven). |
| **DB - Collections** | Unknown (request instances, templates, company users, files metadata persisted by backend APIs not in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `show_regenerate_request` and `disabled_update_request` both intentionally read `disabled_update_request` in `getRequestInstance` (possible copy-paste bug); full server-side validation rules for auto-populate payloads per template ID. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/requests/edit.js`

- **Shell:** `AdminLayout` with `hideDrawer`, `sidebarActiveMenuItemKey="requests"`; breadcrumbs Requests → request id (lines 396–427). `loginToSleekSignPlatform` for embedded signing context (lines 63–72).
- **Load:** `getPlatformConfig` → `getUser` (admin `/admin/users/me`), `getCompany` (share items), `getRequestInstance` → `api.getCompanyRequestInstance(companyId, requestId)`, `getCompanyUsers` (directors + shareholders), `getCorpSecMembers` (`api.getAdminsByGroup` with `CORP_SEC`), `getRegistrableControllers`, `fetchCommonData` (lines 1225–1235, 1251–1267, 1271–1331, 1334–1363).
- **Auto-populate gating:** From CMS `request` → `auto_populate_documents`: `documentRequestTemplateIDs`, `disabled_update_request`, `display_prompt_for_regenerating_auto_templates`, timezone; drives `enabledAutoPopulate`, `disabledUpdateRequestButton`, `showRegenerateButton`, `displayPromptForAutoTemplates` (lines 1276–1297).
- **Regenerate:** `onRegenerateRequest` / `handleRegenerateRequest` → `api.autoPopulateRequestInstance(companyId, requestId, { body: JSON.stringify(buildDataForAutoPopulate(...)) })`; warns when `html_result_override` exists; merges template-specific payloads (nominee notices, board resolutions, share certificates, corp sec consent) with `is_manually_updated`, `isFromAdhoc` flags (lines 76–137, 140–221).
- **Update request:** `handleUpdateRequest` → `handleFormSubmit`; uploads file inputs via `uploadFile` → `viewUtil.uploadFile` to company root; `editRequestInstance` with `client_provided_document`, `document_fields`, `director`, `shareholder`, `company_staff`, `document_name`, `selected_shareholders`, `selected_directors`, `requestFrom`, optional `reset_document` / `html_result_override` / `is_manually_updated` (lines 224–334, 337–339). If `enabledAutoPopulate`, submit delegates to `handleRegenerateRequest` (lines 272–274).
- **Template-bound fields:** `renderFields` switches on CMS template IDs (board resolutions, corp sec consent, nominee director notices, SBA LOA) vs default `extended_doc_template_data.bindedData` for director/shareholder/company staff/share transaction/selected directors (lines 524–584). `FormInputs` + `renderDatepickerFields` for `customVariableConfigs` (text/select/date) (lines 587–721).
- **Document name:** `getDocumentName` special-case for `automated_sba_loa_for_non_directors` appends director first name (lines 251–269).
- **Document editor:** `HtmlEditor` for `html_result`; `handleOnSaveManualChanges` → `handleFormSubmit` with `html_result_override`; `convertHtmlToPdf`, `sendRequestInstanceForSignature` (admin) with HTML + orientation; partner-branded SleekSign labels via `getContentByPriority` / `getPartnerSleekSignBrandLabel` (lines 1141–1214, 1519–1611).
- **Status:** `requestStatusFormHandleSubmit` → `api.changeRequestInstanceStatus` with `status`, `status_remarks`, `send_notification` (lines 1077–1423).
- **Files:** Signed file download/move; `renderLocalPath` warns when PandaDoc path is under `Requests` folder (lines 443–467, 470–520, 1436–1497).

### `src/utils/api.js`

- **`editRequestInstance`:** `PUT ${getBaseUrl()}/admin/request-instances/${requestInstanceId}` (lines 625–627).
- **`autoPopulateRequestInstance`:** `POST ${getBaseUrl()}/admin/companies/${companyId}/request-instances/${requestInstanceId}/auto-populate` (lines 1205–1207).
- **`getCompanyRequestInstance`:** `GET ${getBaseUrl()}/companies/${companyId}/request-instances/${requestInstanceId}` (lines 1180–1182).
- **`changeRequestInstanceStatus`:** `POST ${getBaseUrl()}/request-instances/${requestInstanceId}/change-status` (lines 1210–1212).
- **`convertHtmlToPdf`:** `POST ${getBaseUrl()}/document-templates/convert-html-to-pdf` (lines 1077–1079).
- **`sendRequestInstanceForSignature`:** `POST ${getBaseUrl()}/request-instances/${requestInstanceId}/send-for-signature` (lines 1220–1222).
- **`sendRequestInstanceForSignaturePandadoc`:** `POST ${getBaseUrl()}/request-instances/${requestInstanceId}/send-for-signature/pandadoc` (lines 1230–1232).
- **`getCompanyDirectors` / `getCompanyShareholders`:** `GET ${getBaseUrl()}/companies/${companyId}/company-users` with client-side filter (lines 461–483).
- **`getAdminsByGroup`:** `GET ${getBaseUrl()}/admin/users/admins` (lines 335–337).
