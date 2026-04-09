# Reconcile lost documents with active files

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Reconcile lost documents with active files |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (Sleek Admin role for listing and CSV export; see Open Questions for reconcile routes) |
| **Business Outcome** | After a document is marked lost and recovered from backup, operations can tie the recovery copy to the correct live file record so bookkeeping and file metadata stay aligned with the real storage location. |
| **Entry Point / Surface** | Sleek admin recovery tooling (HTTP API: `GET /admin/recovery/files`, `POST /admin/recovery/reconcile-files`, `POST /admin/recovery/unreconcile-files`; plus `GET /admin/recovery/generate-csv` for lost-file export). Exact in-app navigation not defined in this repo. |
| **Short Description** | Sleek admins browse files under a path and see candidate “lost” files that match by name. They link a recovery file to a target file so the recovery blob is written to the target’s storage key and the link is stored on the recovery record; they can remove that link and clear the target’s recovered flag. Listing and CSV export are restricted to the Sleek Admin role. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **S3** (legacy path: copy from recovery `remote_path` to target `remote_path` via `file-vendor`); **@sleek-sdk/sleek-files** `FileService.reconcileFiles` when the Files microservice toggle is on. Upstream: file loss/recovery labelling (`lost`, `recovered`). Downstream: any flows that read `reconciled_files` or `recovered` on `File`. |
| **Service / Repository** | sleek-back (primary); sleek-files (external implementation when microservice enabled — not inspected here) |
| **DB - Collections** | `File` (MongoDB): reads/updates `reconciled_files` (array of ObjectIds), `recovered` (boolean), and fields used for queries (`lost`, `name`, `local_path`, `type`, etc.). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High (recovery-controller + legacy `reconcileFiles`); Medium for external `FileService.reconcileFiles` behaviour (delegated, implementation not read in this pass) |
| **Disposition** | Unknown |
| **Open Questions** | `POST /admin/recovery/reconcile-files` and `POST /admin/recovery/unreconcile-files` use `userService.authMiddleware` only, while `GET /admin/recovery/files` and `GET /admin/recovery/generate-csv` also require `accessControlService.isIn("Sleek Admin")`. Confirm whether reconcile/unreconcile are intentionally broader than Sleek Admin or an oversight. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`controllers/admin/recovery-controller.js`:**
  - **`GET /admin/recovery/generate-csv`:** `userService.authMiddleware`, `accessControlService.isIn("Sleek Admin")`. Builds CSV from `File.find({ lost: true })`, resolves owner via `User` / `Company` from `local_path`.
  - **`GET /admin/recovery/files`:** Same auth as CSV. Validates query (`local_path`, `name`, `is_recursive`, sort, pagination, `type`). `File.find(...).populate("reconciled_files")`. For each non-folder file, finds `File` documents with same `name`, `lost: true`, `recovered: false` as `matchingFiles`; enriches with `fileService.getFileOwner`. For `reconciled_files`, enriches owners the same way.
  - **`POST /admin/recovery/reconcile-files`:** Body `recovery_file_id`, `target_file_id`. Loads both `File` documents, calls `fileService.reconcileFiles(recoveryFile, targetFile)`.
  - **`POST /admin/recovery/unreconcile-files`:** Same body shape. Removes `target_file_id` from `recoveryFile.reconciled_files`, sets `targetFile.recovered = false`, `Promise.all([recoveryFile.save(), targetFile.save()])`.

- **`services/file-service.js`:** `reconcileFiles(recoveryFile, targetFile)` delegates to `_getService()` (legacy vs `@sleek-sdk/sleek-files` `ExternalFileService` based on Files microservice toggle), then `service.reconcileFiles(recoveryFile, targetFile)`.

- **`services/legacy-services/file-service.js` — `reconcileFiles`:** Reads recovery blob from S3 (`fileVendor.getFileOnS3(recoveryFile.remote_path, ...)`), uploads to `targetFile.remote_path`, appends `targetFile._id` to `recoveryFile.reconciled_files`, sets `targetFile.recovered = true`, saves both files.

- **`schemas/file.js`:** `PopulateModelProxy` default `reconciled_files: []`; model may be `FileModel` from sleek-files when toggle enabled.
