# Electronic signature and signed document handling

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Electronic signature and signed document handling |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations / Admin |
| **Business Outcome** | Staff can finalize request documents, export or send them for electronic signature (SleekSign or legacy PandaDoc flows), open the external signing experience, and after completion download or move signed PDFs into the correct company Secretary file tree. |
| **Entry Point / Surface** | Sleek Admin > **Requests** > open a request (`AdminEditRequestView`, route with `?cid=` and `?rid=`; breadcrumbs to `/admin/requests/`). |
| **Short Description** | On the request edit screen, operators update template-driven fields and HTML output, save manual edits, generate a client-side PDF download, and—when `e_signature.request_document` is enabled—send the HTML to the backend for signature (`send-for-signature`) or open an existing `document_to_sign_url`. Completed runs show `signed_file` with download and a **Move File To…** flow that lists subfolders under `/companies/:companyId/Secretary/` and calls the files service `move` API. |
| **Variants / Markets** | Unknown (partner branding via `getPartnerSleekSignBrandLabel`; tenant `platformConfig` gates e-signature and auto-populate; not hard-coded to a single market in this view) |
| **Dependencies / Related Flows** | Request instance lifecycle (`getCompanyRequestInstance`, `editRequestInstance`, `changeRequestInstanceStatus`, `autoPopulateRequestInstance`); HTML→PDF (`convertHtmlToPdf`); signature orchestration on main API (`sendRequestInstanceForSignature`, optional legacy `sendRequestInstanceForSignaturePandadoc`); Files microservice (`getFileBaseUrl`, `getFiles`, `moveFile`); SleekSign iframe auth (`loginToSleekSignPlatform`, `SLEEK_SIGN_URL`). Backend persistence and webhooks for PandaDoc/SleekSign—out of repo. |
| **Service / Repository** | `sleek-website`: `src/views/admin/requests/edit.js`, `src/utils/api.js`. Main API (`getBaseUrl()`), Files service (config-driven `getFileBaseUrl()`). |
| **DB - Collections** | Unknown (request instances, files metadata, signature state maintained by APIs not in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `handleClickSendToPandadoc` remains reachable from any UI path (defined on class; primary send path uses `sendRequestInstanceForSignature`); exact backend rules for when `document_to_sign_url` is PandaDoc vs SleekSign (`is_sleek_sign`). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/requests/edit.js`

- **Admin shell:** `AdminLayout` with `sidebarActiveMenuItemKey="requests"`, toolbar breadcrumbs **Requests** → current `requestId` (lines 396–427).
- **Request load:** `getRequestInstance` → `api.getCompanyRequestInstance(companyId, requestId)`; hydrates form state, auto-populate flags from CMS `auto_populate_documents`, `html_result` for editor (lines 1271–1331).
- **Signing links (legacy + current):** Request details render **Pandadoc file URL** as `document_to_sign_url` (lines 508–514). When `signed_file` exists: name, **Download**, shortened `local_path` with warning if under **Requests** folder (`renderLocalPath`, lines 443–467, 470–516).
- **Move signed file:** **Move File To…** → `api.getFiles` with `local_path` `/companies/${companyId}/Secretary/`, `type: folder`; confirm → `api.moveFile(fileId, { body: JSON.stringify({ destination_folder }) })` (lines 1441–1497).
- **Document editor / PDF / send:** `renderDocumentEditor` gated by `e_signature.props.request_document.enabled`. For generated HTML (no `client_provided_document`): `HtmlEditor`, **Save changes** (`handleOnSaveManualChanges` → `editRequestInstance` with `html_result_override`), **Save as PDF** → `api.convertHtmlToPdf` with `buildDocumentOrientation` (lines 1141–1214, 1520–1538). **Send to SleekSign** (partner label when set) when no `document_to_sign_url` → `api.sendRequestInstanceForSignature` with `htmlToConvert` + orientation (lines 1165–1174, 1577–1611). After URL exists: **View on SleekSign** / **View on Pandadoc** from `requestInstance.is_sleek_sign` → `handleClickViewOnSleekSign` (v2 opens URL per `admin_sleek_sign_url_version`, else `window.open`) (lines 1176–1574).
- **Custom document path:** If `client_provided_document` is set, section title becomes **Document Signature** and editor is hidden; upload/update flows use `editRequestInstance` and file upload helpers (lines 1185–1200, 272–335, 337–339).
- **Other:** `loginToSleekSignPlatform` in constructor for iframe SSO to SleekSign (lines 63–72). `handleClickSendToPandadoc` calls `sendRequestInstanceForSignaturePandadoc` (lines 1614–1643)—legacy PandaDoc send path.

### `src/utils/api.js`

- **Request instances:** `getCompanyRequestInstance` → `GET ${getBaseUrl()}/companies/${companyId}/request-instances/${requestInstanceId}` (lines 1180–1182). `editRequestInstance` → `PUT ${getBaseUrl()}/admin/request-instances/${requestInstanceId}` (lines 625–627). `autoPopulateRequestInstance` → `POST …/admin/companies/${companyId}/request-instances/${requestInstanceId}/auto-populate` (lines 1205–1207). `changeRequestInstanceStatus` → `PUT …/request-instances/${requestInstanceId}/change-status` (lines 1210–1212).
- **PDF:** `convertHtmlToPdf` → `POST ${getBaseUrl()}/document-templates/convert-html-to-pdf` (lines 1077–1079).
- **Signature:** `sendRequestInstanceForSignature` → `POST ${getBaseUrl()}/request-instances/${requestInstanceId}/send-for-signature` (lines 1220–1222). `sendRequestInstanceForSignaturePandadoc` → `POST …/send-for-signature/pandadoc` (lines 1230–1232).
- **Files:** `getFileBaseUrl()` (main API or Files MS per `files_microservice` config) (lines 56–84). `getFiles` → `${getFileBaseUrl()}/files` (lines 926–928). `moveFile` → `POST ${getFileBaseUrl()}/files/${fileId}/move` (lines 1027–1029).
