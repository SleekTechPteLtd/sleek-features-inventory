# Manage document request pipeline

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage document request pipeline |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operations staff can find request instances, correct signer and field data, push documents into Sleek Sign (or legacy PandaDoc), advance workflow status with optional client email, and resolve instances from a signature document id so incorporation and company-secretary document flows stay on track. |
| **Entry Point / Surface** | Sleek Admin / back-office (HTTP API under `/admin/request-instances`, `/admin/request-instance/:documentId`, and nested routes such as `.../change-status`, `.../send-for-signature`) |
| **Short Description** | Authenticated users with **requests** permissions list and filter request instances (status, company, id list, pagination), update instance payload (signer refs, `document_fields`, folder, HTML override, etc.), send generated or uploaded PDFs to signature providers, post status changes with optional `REQUEST_STATUS_CHANGED` emails to owners/requesters, and look up an instance by Sleek Sign `document_id`. Supporting routes cover printing-service batches and company-scoped auto-populate for templated documents. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Request templates** and **document templates** (instance content and signers); **signature** integration (`signatureService.createDocumentFromPDF` / PandaDoc variant); **file** storage and folders; **company** sub-status updates after send-for-signature; **partner** for MS client links; **mailer** transactional templates; **company-user** / **user** for recipients; **Camunda/app features** and incorporation template IDs for signer rules. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `requestinstances` (Mongoose `RequestInstance`); reads/writes also touch `companies`, `companyusers`, `users`, `files`, `partners`, `companyworkflows`, `documenttemplates`, `requesttemplates` via populate and related queries |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `GET /admin/request-instance/:documentId` returns JSON `{ companyId }` but assigns `requestInstance.document_id` to that field—naming or contract mismatch? That route has no `authMiddleware` in code; confirm intended exposure for Sleek Sign callbacks or embeds. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Auth / permissions**: Routes use `userService.authMiddleware` with `accessControlService.can("requests", "read" | "edit" | "full")` as appropriate (`read` for list/printing reads; `full` for updates, signature sends, status changes; `edit` for generate-document-name and mark-as-printed).

- **List / filter**: `GET /admin/request-instances` validates query (`status` as array, `company`, `request_instances` ids, `skip`/`limit`); builds Mongo query with `$in` for status and ids; default limit from `sharedData.requestInstances.limitPerSearch`; sorts `createdAt` desc; populates `company` and file fields for signed files.

- **Update instance (signers, fields, etc.)**: `PUT /admin/request-instances/:requestInstanceId/` merges `document_fields`, `director`, `shareholder`, `company_staff`, `client_provided_document` (with file move into `request_folder`), `document_name`, `excluded_company_users`, `selected_shareholders` / `selected_directors`, `selected_folder_id`, `html_result_override` / `reset_document`, `is_manually_updated`.

- **Sleek Sign / signature**: `POST .../send-for-signature` builds PDF from HTML, resolves signers via `documentTemplateService.getSignersWithTags` with template-specific custom signer logic, calls `signatureService.createDocumentFromPDF`, sets `document_id`, `pandadoc_id`, `document_to_sign_url`, `status: waiting_for_signatures`, `is_sleek_sign`; `POST .../send-file-for-signature` creates instance and uses `requestInstanceService.createRequestFolder` then `signatureService.createDocumentFromPDF` from client PDF; `POST .../send-for-signature/pandadoc` uses `signatureService.createDocumentFromPDF_pandadoc` and PandaDoc view URL.

- **Status + optional notification**: `POST /admin/request-instances/:requestInstanceId/change-status` validates status against `sharedData.requestInstances.status`, saves `status` and `status_remarks`; if `send_notification`, `mailerService.sendEmail(config.mailer.templates.REQUEST_STATUS_CHANGED, {...}, recipients, options)` to company owner and requester when distinct.

- **Lookup by signature document id**: `GET /admin/request-instance/:documentId` — `RequestInstance.findOne({ document_id: documentId })` (no auth in controller).

- **request-instance-service.js**: `createRequestFolder`, `getSelectedDirectors` (used when building signer context for PDF flow); middleware and helpers elsewhere not all exercised by this admin controller.

- **mailer-service.js**: `sendEmail(templateId, variables, recipients, options)` delegates to mailer vendor (transactional email).

- **schemas/request-instance.js**: `RequestInstance` — `request_template`, `company`, signatory refs, `document_fields`, files, `status` / `status_remarks`, `document_id` / `pandadoc_id`, `document_to_sign_url`, `is_sleek_sign`, `html_result_override`, `event_history` on status change, printing-service fields; indexes on `company`, `status`, `document_id`, etc.

- **Files**: `controllers/admin/request-instance-controller.js`, `services/request-instance-service.js`, `services/mailer-service.js`, `schemas/request-instance.js`.
