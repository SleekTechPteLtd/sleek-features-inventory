# Manage risk assessment customer acceptance

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage risk assessment customer acceptance |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, Compliance (requestors submit; approvers receive notifications and act on pending items) |
| **Business Outcome** | Customer acceptance for company onboarding risk assessment is captured, progressed, and auditable so compliance can approve, reject, or request more information with file evidence and workflow linkage. |
| **Entry Point / Surface** | `sleek-back` HTTP API under `userService.authMiddleware`: `POST /v2/risk-assesment-form/customer-acceptance/:companyId` (create or update), `GET /v2/risk-assesment-form/company-acceptance-form/:id` (detail + logs). Customer acceptance state is also returned on `POST /v2/risk-assesment-form/compute-score/:companyId`. Exact Sleek app / Admin navigation labels are not defined in these files. |
| **Short Description** | Requestors create or update a per-company customer acceptance record (status, message, approver list, file references). On create or when status is `pending`, emails go to named approvers (and configured CC defaults) via configurable templates; non-pending resolutions notify the requestor. Each action appends rows to an acceptance log. When the company has incorporation RAF workflow data, the acceptance document id is written to `CompanyWorkflow.data.incorporation_raf.company_acceptance_form`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **App features**: `kyc_raf` / `authenticated` → `raf_customer_acceptance` (default approver CC list). **External**: `mailer-vendor` (`KYC_RAF_REQUEST_FORM_APPROVAL`, `KYC_RAF_CUSTOMER_ACCEPTANCE_*` templates), `file-service` + `File` schema for email attachments, `config.sleekAdminBaseUrl` workflow links in email variables. **Related**: KYC RAF compute-score flow returns `customer_acceptance` alongside RAF sections; incorporation `CompanyWorkflow` links the acceptance form id. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | Mongoose models `RiskAssesmentCustomerAcceptance` and `riskAssesmentCustomerAcceptanceLogs` (MongoDB default pluralised collection names); reads/writes also reference `Company`, and when linking workflow, `CompanyWorkflow`; `File` loaded for attachment payloads in outbound mail. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/risk-assesment-form.js`

- **`POST /customer-acceptance/:companyId`** (`userService.authMiddleware`): Loads `Company` with `incorporation_workflow`, existing `RiskAssementCustomerAcceptance` with `requestor` populated. Reads `kyc_raf` / `authenticated` app feature for `raf_customer_acceptance.value.default_approver`. **Create path**: `RiskAssementCustomerAcceptance.create` with `approver`, `files`, `message`, `company`, `status`, `requestor: req.user._id`; loops approvers with email and calls `kycRAFServices.sendEmailNotificationToComplianceCustomerAcceptance` (with `filterApprovers` for CC); `RiskAssementCustomerAcceptanceLogs.create` for “sent a request for approval…”. **Update path**: assigns `status`, `message`, `approver`, `files`; if `status === "pending"`, re-sends approver emails and logs; else logs resolution (`approved` / `rejected` / `need_more_info`) and emails requestor via `sendEmailNotificationToComplianceCustomerAcceptance`. If `company.incorporation_workflow.data.incorporation_raf`, updates `CompanyWorkflow` with `data.incorporation_raf.company_acceptance_form` = `response.data._id`.
- **`GET /company-acceptance-form/:id`**: `RiskAssementCustomerAcceptance.findById` + `RiskAssementCustomerAcceptanceLogs.find({ company })` sorted by `updatedAt`.
- **`POST /compute-score/:companyId`**: Loads `RiskAssementCustomerAcceptance` and `RiskAssementCustomerAcceptanceLogs`; includes `customer_acceptance: { data, logs }` in JSON response.

### `services/kyc-risk-assesment-form.js`

- **`sendEmailNotificationToComplianceCustomerAcceptance`**: Builds `variables` (`company_name`, `approver_name`, `redirection_url` from admin workflow URL, `message`, `requestor_name`); optional `File.find` + `fileService.getFile` for base64 attachments; `mailerVendor.sendEmail` with template map by `status` (`pending` → `KYC_RAF_REQUEST_FORM_APPROVAL`, `approved`, `need_more_info`, `rejected`), `config.customer.emails` as sender, recipient `[email]`, CC `config.compliance.emails` plus CC list.

### `schemas/risk-assesment-customer-acceptance.js`

- **Fields**: `status` enum from `CUSTOMER_ACCEPTANCE` (`approved`, `rejected`, `pending`, `need_more_info`); `approver` array; `requestor` → `User`; `files` → `[File]`; `message`; `company` → `Company`; `timestamps: true`.

### `schemas/risk-assesment-customer-acceptance-log.js`

- **Fields**: `remarks`, `action`, `user` → `User`, `company` → `Company`; `timestamps: true`.

### `constants/risk-assesment-form.js`

- **`CUSTOMER_ACCEPTANCE`**: `['approved', 'rejected', 'pending', 'need_more_info']`.

### `app-router.js`

- Router mount: **`/v2/risk-assesment-form`** → `controllers-v2/risk-assesment-form`.
