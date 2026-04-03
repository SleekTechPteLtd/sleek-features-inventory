# Complete Employment Pass employee application

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Complete Employment Pass employee application |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Registered user (employee / applicant completing the Singapore Employment Pass form on behalf of the engagement) |
| **Business Outcome** | The client supplies all required Employment Pass information and documents in one guided flow so Sleek can lodge and process the pass request with accurate, complete data. |
| **Entry Point / Surface** | **sleek-website** public flow: **`/ep/?epid=<EP id>`** with optional **`cs=<1–6>`** (current step) and **`ar=1`** (admin review mode — skips validation/saves for non-admin viewers). Linked from admin as **Review Form** (`/ep/?epid=…&ar=1`). Logo links to **`/dashboard/`**. |
| **Short Description** | Six-step wizard (**Application Info**, **Personal Info**, **Education**, **Employment**, **Declaration**, **Confirmation**) with a step trail, **Previous** / **Next** / **Submit Application**, and copy explaining auto-save after each step. Each step **PUT**s partial data to the EP record; steps with files upload to the user’s file root (**5 MB** max per file) then persist file IDs. Final step **POST**s submission. After submit, status is no longer **draft** and a success message is shown. Unverified users are redirected to **`/verify/`**; **`422 Unprocessable Entity`** on load shows **No Access**. |
| **Variants / Markets** | **SG** (Employment Pass is Singapore-specific). |
| **Dependencies / Related Flows** | **Backend**: **`GET/PUT /eps/:id`**, **`POST /eps/:id/submit`** (sleek-back). **Files**: **`viewUtil.uploadFile`** → user **`root_folder`** (files microservice). **Admin**: EP creation via **`createEp`** (`POST` with **`admin: true`**) in **`admin/ep/index.js`**; staff read-only **`/admin/ep/edit`**. Applicant must have an **`epid`** (created upstream — not in this view). |
| **Service / Repository** | **sleek-website**: `src/views/ep.js` (`EPView`), `src/utils/api.js` (`getUser`, `getEp`, `updateEp`, `submitEp`). **sleek-back**: EP REST API. **Files service**: uploads referenced by `src/utils/view.js` (`uploadFile` / `downloadFile`). |
| **DB - Collections** | Unknown (EP documents live in backend; not defined in sleek-website). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | **`paymentOk`** and **`editCompanyPostPayment`** appear in UI logic but are never set in this file — legacy or unfinished integration? Exact files-API contract and virus/size limits beyond the client message. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/ep.js` (`EPView`)

- **Bootstrap**: Query **`cs`** → **`currentStep`** (default **1**); **`epid`** → **`epId`**; **`ar`** → **`adminReview`**. **`maxStep = 6`**.
- **Steps**: Trail labels **Application Info**, **Personal Info**, **Education**, **Employment**, **Declaration**, **Confirmation** — `renderStep1FormContent` … `renderStep6FormContent`.
- **Mount**: **`api.getUser`** → unverified → **`/verify/`**; if **`adminReview`** and user is not **`profile === "admin"`**, **`adminReview`** is cleared. Then **`getEp()`** if **`epId`** set.
- **`getEp`**: **`api.getEp(epId)`** → merge **`ep.data`** into **`formValues`**. Error **`Unprocessable Entity`** → **`noAccess`**.
- **Draft vs submitted**: Renders form when **`ep.status === "draft"`** or **`adminReview === true`**; otherwise **`renderSuccessCard`** (“We have received your Employment Pass application”).
- **Saves**: **`submitForm1`**–**`submitForm5`** call **`api.updateEp(epId, { body: JSON.stringify(...) })`** with step-specific **`pick`** fields; **`submitForm6`** → **`api.submitEp(epId)`** then **`getEp()`**.
- **Files**: **`uploadFilesFromFileInputs`** → **`uploadFile`** via **`viewUtil.uploadFile(file, user.root_folder, { maxMb: 5 })`**; **`flattenFiles`** maps **`_files`** keys to file ID arrays before PUT.
- **Inline edits**: Removing/editing education, membership, or employment rows triggers **`updateEp`** with the relevant collection key.
- **Navigation**: **`handleClickTrailStep`** changes step without persisting; **`goToNextStep`** after successful step save.

### `src/utils/api.js`

- **`getEp`**: **`GET ${getBaseUrl()}/eps/${epId}`**
- **`updateEp`**: **`PUT ${getBaseUrl()}/eps/${epId}`**
- **`submitEp`**: **`POST ${getBaseUrl()}/eps/${epId}/submit`**

### Related

- **`src/views/admin/ep/index.js`**: creates EPs with **`api.createEp`** (not the applicant flow in `ep.js`).
- **`src/utils/view.js`**: **`uploadFile`** / **`downloadFile`** / **`showResponseErrorAlert`** used by the flow.
