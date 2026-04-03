# Report and investigate lost files

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Report and investigate lost files |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (Sleek Admin role for browse and CSV export; authenticated user for reconcile/unreconcile POST — see Open Questions) |
| **Business Outcome** | Operations can see which stored files are marked lost, export that inventory, find candidates to restore content, and link recovery copies to real file records so customer documents stay consistent. |
| **Entry Point / Surface** | Backend **sleek-back** admin routes under `/admin/recovery/*` (consumed by Sleek admin tooling or internal UIs — not a standard end-user Sleek App path). |
| **Short Description** | **CSV export** lists all documents with `lost: true` with folder, owner type/name, timestamps, recovered flag, and id. **Browse/search** supports path and name filters (optional recursion), sorting, pagination, and type (file vs folder); each file row is enriched with **matching** lost files (same name, still lost and not recovered) and populated **reconciled** targets plus owner resolution. **Reconcile** copies the recovery file’s S3 payload onto the target file and marks the target recovered; **unreconcile** removes the link and clears recovered on the target. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **MongoDB** `File` documents (`lost`, `recovered`, `reconciled_files`, `local_path`, `name`, types `file_s3` / `encrypted_s3`); **User** and **Company** for owner labels in CSV and `getFileOwner`. **file-service** delegates `reconcileFiles` / `getFileOwner` to **legacy** implementation or **@sleek-sdk/sleek-files** when the files microservice toggle is on. **AWS S3** (legacy path): recovery binary read from recovery file `remote_path`, upload to target `remote_path`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `files` (Mongoose model `File`), `users`, `companies` (owner resolution for CSV and populated metadata) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `POST /admin/recovery/reconcile-files` and `POST /admin/recovery/unreconcile-files` use `authMiddleware` only and do **not** apply `accessControlService.isIn("Sleek Admin")`, unlike the GET routes — confirm whether this is intentional for service accounts or an oversight. Exact admin UI navigation label is not defined in this repo. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`controllers/admin/recovery-controller.js`:**
  - **GET `/admin/recovery/generate-csv`** — `userService.authMiddleware`, `accessControlService.isIn("Sleek Admin")`. `File.find({ lost: true })`, builds CSV header `file,folder,type,owner,created,modified,recovered,id`, resolves folder from `local_path`, owner via `User` or `Company` by path segment, sets `Content-Disposition: attachment; filename=recovery.csv`.
  - **GET `/admin/recovery/files`** — same admin guards. Validates query: `is_recursive`, `local_path`, `name`, `sort_by` (`createdAt` \| `updatedAt` \| `name`), `sort_order` (1 \| -1), `limit`, `skip`, `type` (`file` \| `folder`). Builds regex on `local_path` / `name` with `escape-string-regexp`, `fileService.cleanName` for name; maps `type: "file"` to `["file_s3", "encrypted_s3"]`. `File.find(findOptions).populate("reconciled_files").sort(...).skip().limit()` (default limit 200). For each non-folder file, finds `File.find({ name, lost: true, recovered: false })` as **matchingFiles** with `fileService.getFileOwner`; populates owner fields on `reconciled_files`. Response `{ files, count }`.
  - **POST `/admin/recovery/reconcile-files`** — body `recovery_file_id`, `target_file_id`; loads both `File` documents; `fileService.reconcileFiles(recoveryFile, targetFile)`.
  - **POST `/admin/recovery/unreconcile-files`** — same ids; removes target from `recoveryFile.reconciled_files`, sets `targetFile.recovered = false`, saves both.

- **`services/file-service.js`:**
  - `cleanName` — strips path-unsafe characters for search terms.
  - `getFileOwner` — routes to external `ExternalFileService` + `User`/`Company` lookup when files microservice enabled, else `LegacyFileService.getFileOwner`.
  - `reconcileFiles` — delegates to active implementation (legacy or external).

- **`services/legacy-services/file-service.js` (`reconcileFiles`):**
  - Reads recovery file from S3 (`fileVendor.getFileOnS3` / `uploadFileOnS3`), appends `targetFile._id` to `recoveryFile.reconciled_files`, sets `targetFile.recovered = true`, saves both.

- **`schemas/file.js` / `schemas/file/file.model.js`:**
  - Mongoose model **`File`**; defaults include `reconciled_files`, `potential_match_files` arrays.
