# Manage request templates

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage request templates |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin operator (Sleek Admin session; unverified users redirected to `/verify/`) |
| **Business Outcome** | Lets internal operators define which document-backed request types appear on the client request flow, whether each is shown, and what extra fields clients must fill—keeping marketing and ops control over templates without code changes. |
| **Entry Point / Surface** | Sleek Admin — **Request Templates** (`/admin/request-templates/`; `sidebarActiveMenuItemKey` `request-templates`; webpack entry `admin/request-templates` → `src/views/admin/request-templates.js`) |
| **Short Description** | Admins list request templates (name, linked document template, visibility, signer type, created date), create or edit a template with name, required document template selection (manual vs automated groups in the dropdown), a visibility switch, and repeatable additional fields (name + type: text, number, date, file). They remove templates after confirmation. Create/update sends `name`, `document_template`, `is_visible`, and `additional_fields` to the API. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** `api.getUser` for session; `api.getDocumentTemplates({ admin: true })` to populate document template options (names prefixed `[AUTOMATED]` / `AUTOMATED` grouped separately). **CRUD:** REST `${getBaseUrl()}/request-templates` — list via `getRequestTemplates()`; create `POST` with `{ admin: true }` → `/admin/request-templates`; update/delete by id with `{ admin: true }` → `/admin/request-templates/:id`. **Downstream:** client-facing request forms and request instances that consume templates (`create-client-request-instances-from-templates` and related flows). Persistence and collection names live in the API service (not in this repo). |
| **Service / Repository** | `sleek-website` — `src/views/admin/request-templates.js`, `src/utils/api.js` |
| **DB - Collections** | Unknown (request template records are stored by the service behind `/request-templates`; no Mongo schemas in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `signers_type` is shown in the list and copied into edit state but is not included in the create/update JSON body in `handleFormSubmit`—confirm whether signer type is immutable, set only server-side, or omitted by oversight. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/request-templates.js`

- **Layout:** `AdminLayout` with `hideDrawer`, `sidebarActiveMenuItemKey="request-templates"`.
- **Load:** `componentDidMount` → `getUser`, `getRequestTemplates` (`api.getRequestTemplates`), `getDocumentTemplates` (`api.getDocumentTemplates({ admin: true })`).
- **List:** Table shows name, resolved document template name, `is_visible`, `signers_type` (title-cased), `createdAt`; **Edit** / **Remove** per row.
- **Remove:** Confirmation dialog → `api.deleteRequestTemplate(id, { admin: true })` → `getRequestTemplates()`.
- **Form:** Name, document template `select` (options split into manual vs `[AUTOMATED]` / `AUTOMATED` name prefixes), `is_visible` checkbox, **Additional Fields** with name + type (`string` \| `number` \| `date` \| `file`) and add/remove rows.
- **Submit:** `handleFormSubmit` → JSON body `{ name, document_template, is_visible, additional_fields }` → `api.updateRequestTemplate(id, …)` or `api.createRequestTemplate(…)` both with `{ admin: true }`.

### `src/utils/api.js`

- `getRequestTemplates` → `GET ${getBaseUrl()}/request-templates` (no `admin` flag in the view call).
- `getRequestTemplate` → `GET …/request-templates/:id`
- `createRequestTemplate` → `POST …/request-templates` (with `admin: true` → `/admin/request-templates`)
- `updateRequestTemplate` → `PUT …/request-templates/:id` (with `admin: true` → `/admin/request-templates/:id`)
- `deleteRequestTemplate` → `DELETE …/request-templates/:id` (with `admin: true`)

### Navigation (in-repo)

- `src/components/new-admin-side-menu.js`, `src/components/admin-side-menu.js`: **Request Templates** → `/admin/request-templates/`.
- `webpack/paths.js`: entry `admin/request-templates` → `./src/views/admin/request-templates.js`.
