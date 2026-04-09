# Send Companies House acknowledgements

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Send Companies House acknowledgements |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Authenticated user (UK incorporation / Companies House flow) |
| **Business Outcome** | Lets users submit acknowledgement correspondence to Companies House during incorporation so the filing process can continue in line with CH requirements. |
| **Entry Point / Surface** | Sleek customer app — UK Companies House incorporation workflow; backend `POST /company-house/send-acknowledgement` (exact screen or step labels are not defined in these handlers). |
| **Short Description** | Authenticated users POST a payload that is forwarded unchanged to the **sleek-company-house** integration service (`POST …/api/send-acknowledgement`), which performs the outbound Companies House acknowledgement step. No company-scoped permission middleware runs on this route beyond session auth. |
| **Variants / Markets** | UK |
| **Dependencies / Related Flows** | **sleek-company-house** microservice (`config.sleekCompanyHouse.baseUrl`). **Related in same module**: `POST /company-house/:companyId/send-application`, `GET /company-house/:id/get-company-status`, document retrieval and status updates — same UK incorporation surface. |
| **Service / Repository** | sleek-back; sleek-company-house (downstream HTTP API) |
| **DB - Collections** | None in sleek-back for this handler (pass-through proxy only; persistence may occur in sleek-company-house). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Full request body contract for `send-acknowledgement` (logs reference `transaction_id`); confirm product UI copy and when this is shown relative to `send-application` and status polling. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `app-router.js`

- Router mounted at **`/company-house`** → `require("./modules/sleek-company-house/controller/company-house-controller")`.

### `modules/sleek-company-house/controller/company-house-controller.js`

- **`POST /send-acknowledgement`** (full path **`POST /company-house/send-acknowledgement`**) — `userService.authMiddleware` only (no `canManageCompanyMiddleware`). Handler **`sendAcknowledgement`**: `companyHouseService.sendAcknowledgement(reqBody)` → `res.json(companyHouseRes)`; errors logged with `transaction_id` from body; **422** on failure.

### `modules/sleek-company-house/services/company-house-service.js`

- **`sendAcknowledgement(payload)`**: `postResource` to **`${config.sleekCompanyHouse.baseUrl}/api/send-acknowledgement`** with `data: payload`. No Mongoose or MongoDB usage in this function.

### Unknown columns (reason)

- **Usage Confidence**: No dedicated tests or call sites for `sendAcknowledgement` were found in the sampled grep; behaviour is clear from the proxy but end-user frequency is not quantified in-repo.
