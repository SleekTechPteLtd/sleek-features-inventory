# Manage request templates

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage request templates |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operations can define and maintain reusable request templates tied to document templates so client-facing request flows stay consistent, visible where intended, and structurally safe when already in use. |
| **Entry Point / Surface** | Sleek Admin / back-office (HTTP API: `POST`, `PUT`, `DELETE` on `/admin/request-templates` and `/admin/request-templates/:requestTemplateId`) |
| **Short Description** | Authenticated admin users with full **requests** permission create request templates linked to a document template, with optional additional field definitions and a visibility flag. Updates are allowed with constraints when at least one request instance exists: `additional_fields` shape (names and types) and `document_template` cannot change; otherwise the template can be edited. Deletion is blocked while any request instance references the template. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Depends on **document templates** (`DocumentTemplate` must exist for create/update). Governs **request instances** (`RequestInstance.request_template`): usage blocks destructive or structural edits and delete. Related: company/user request flows that materialize instances from templates. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `requesttemplates`, `requestinstances`, `documenttemplates` (Mongoose models `RequestTemplate`, `RequestInstance`, `DocumentTemplate`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | POST validates `client_provided_document` and `document_fields` but the controller does not persist them on create—intentional API evolution or omission? Schema fields `is_multiple_shareholder`, `is_multiple_registrable_controller`, and soft-delete `is_deleted` are not set by this controller. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Auth and permission**: All routes use `userService.authMiddleware` and `accessControlService.can("requests", "full")` — full request permission on the admin surface.

- **POST** ` /admin/request-templates`: Validates `name`, `document_template` (required), optional `client_provided_document`, `document_fields`, `additional_fields` (array), `is_visible` (required). Loads `DocumentTemplate` by id; creates `RequestTemplate` with `name`, resolved `document_template`, `additional_fields`, `is_visible`. Errors return HTTP 422.

- **PUT** `/admin/request-templates/:requestTemplateId`: Loads template; validates partial body (`name`, `document_template`, `additional_fields`, `is_visible`). If any `RequestInstance` exists for this template, rejects changes to `additional_fields` (name/type multiset) or `document_template`; otherwise allows merge and `save()`.

- **DELETE** `/admin/request-templates/:requestTemplateId`: Rejects if any `RequestInstance` references the template (`Existing request instance in use!`); else `RequestTemplate.deleteOne`.

- **Schemas**: `schemas/request-template.js` — `document_template` ref, `additional_fields` (typed `name`/`type` from `sharedData.requestTemplate.additional_fields.type`), `is_visible`, flags for multiple shareholder/registrable controller, `is_deleted`. `schemas/request-instance.js` — `request_template` indexed ref, `additional_fields` with files/values for instances. `schemas/document-template.js` — template metadata used as the link target.

- **Files**: `controllers/admin/request-template-controller.js`, `schemas/request-template.js`, `schemas/request-instance.js`, `schemas/document-template.js`.
