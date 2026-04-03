# Track physical printing fulfillment

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Track physical printing fulfillment |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operations can see which completed document requests are due for physical printing by folder and week, confirm a folder batch is fully printed, and record print completion so fulfillment state stays accurate. |
| **Entry Point / Surface** | Sleek Admin / back-office (HTTP API under `/admin/request-instances/printing-service` and `/admin/request-instances/printing-service/mark-as-printed`) |
| **Short Description** | Lists successful request instances for a **printing service folder** type (`COMPANY_DOCS` or `ADDRESS_LABEL`) within a **week window** (`start_of_week` / `end_of_week` query params). A separate endpoint reports whether any items in that slice are still **not printed**, so staff can verify a folder is fully printed before closing a batch. Marking as printed updates `printing_service_status` to **PRINTED** for selected request instance ids (body field `fileIds`). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Request instances** must already have `printing_service_date`, `printing_service_folder`, and typically `printing_service_status` (e.g. **NOT_PRINTED**) set upstream—evidenced when UK incorporation workflow sends documents to the printing queue (`services/camunda-workflow/uk-incorporation/uk-incorporation-service.js`). Broader admin **request instance** listing and status flows (`/admin/request-instances`) are adjacent. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `requestinstances` (Mongoose model `RequestInstance`: `printing_service_date`, `printing_service_status`, `printing_service_folder`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Are `printing_service_*` fields populated for non-UK flows elsewhere? Request body uses `fileIds` but `updateMany` targets `_id` on `RequestInstance`—confirm client naming vs intent. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Auth and permission**: `GET` printing-service routes use `userService.authMiddleware` and `accessControlService.can("requests", "read")`. `POST .../mark-as-printed` uses `can("requests", "edit")`.

- **GET** `/admin/request-instances/printing-service`: Query `folder_type`, `start_of_week`, `end_of_week`. Finds `RequestInstance` with `printing_service_folder`, `printing_service_date` within range, `status: "success"`, sorted `createdAt` desc. Populates `company`. Returns JSON array.

- **GET** `/admin/request-instances/printing-service/folder-print-status`: Same folder and date range; `findOne` where `printing_service_status` is `NOT_PRINTED`. Response `{ has_printed_all_documents: result ? false : true }` (no unprinted → `true`).

- **POST** `/admin/request-instances/printing-service/mark-as-printed`: Body `fileIds` (array, required). `RequestInstance.updateMany({ _id: { $in: bodyCleaned.fileIds } }, { $set: { printing_service_status: PRINTED } })`.

- **Constants** (`constants/request-instance-constants.js`): `PRINTING_SERVICE_STATUS` (`NOT_PRINTED`, `PRINTED`); `PRINTING_SERVICE_FOLDER` (`COMPANY_DOCS`, `ADDRESS_LABEL`).

- **Schema** (`schemas/request-instance.js`): Indexed sparse fields `printing_service_date`, `printing_service_status`, `printing_service_folder`.

- **Tests**: `tests/controllers/request-instance-controller/printing-service.test.js` exercises printing-service behavior.

- **Files**: `controllers/admin/request-instance-controller.js` (printing-service block ~686–725), `constants/request-instance-constants.js`.
