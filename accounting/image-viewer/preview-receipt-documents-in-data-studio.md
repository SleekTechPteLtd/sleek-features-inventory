# Preview receipt documents in Data Studio

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Preview receipt documents in Data Studio |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Verified accountant (accounting team member via BigQuery allowlist) |
| **Business Outcome** | Accounting staff can open receipt PDFs and images from cloud storage in an embedded viewer inside Data Studio workflows without exposing files to unauthenticated users. |
| **Entry Point / Surface** | Data Studio / GDS workflows that embed the Sleek Receipts service; HTTP surface is `GET /image/view` on the Receipts app (mounted at `/image` in `index.js`). |
| **Short Description** | Authenticated GET endpoint: validates the caller’s email against Google BigQuery “accounting team incharge” tables, loads the object from the receipts S3 bucket using a `file_url` query parameter, then returns minimal HTML embedding the file as a data URL—PDFs in an iframe, raster images in an `<img>`—so the browser can render the document inline. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** Receipt files stored under `RECEIPTS_S3_BUCKET` with keys scoped by `NODE_ENV`. **Auth:** BigQuery project `BQPROJECTID_V2` with credentials from `BIGQUERY_CREDENTIALS`; production queries `gds_views.tb_team_incharge` (team lead / manager / bookkeeper emails); non-production uses `test.tb_accounting_team_incharge`. **Client:** Data Studio only (comment on route). Related: general receipt upload/storage elsewhere in Sleek Receipts (`FileUploader`). |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | None (authorization reads BigQuery; file bytes from S3) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Controller notes this image viewer is temporary and may be removed; confirm product roadmap and any replacement. Whether non-SG markets use the same BQ allowlist is not stated in code. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/routes/image-viewer.js`**
  - `GET /view` → `validateImageViewerAuth()`, `ImageViewerController.viewImage`. Comment: only used in Data Studio.

- **`src/middleware/image-viewer-middleware.js`**
  - `validateImageViewerAuth`: requires `query.email`; uses `authBQV2()` and `getAccountantName(BQInstance, projectId, email)`; proceeds only if the query returns a non-empty row, otherwise `ERRORS.AUTH_ERROR`.

- **`src/bigquery/bigquery-utilities.js`** (supporting auth)
  - `getAccountantName`: production unions team lead / manager / bookkeeper emails from `${projectId}.gds_views.tb_team_incharge` with `@sleek.sg` → `@sleek.com` replacement; else `test.tb_accounting_team_incharge` for non-production.

- **`src/controllers/image-viewer.controller.js`**
  - `viewImage`: reads `file_url` from query; derives S3 key from substring after `` `${NODE_ENV}/` ``; `FileUploader.getFileOnS3(filePath, RECEIPTS_S3_BUCKET, true)`; `fileUtils.encodeDocument` with S3 `ContentType` for data-URL MIME; PDF → iframe HTML, else `<img>` with data URL; empty `file_url` → 200 empty; errors → 422.

- **`src/files/uploader.js`**
  - `getFileOnS3(path, bucket, bypassUTF)`: `s3.getObject`, returns full response when `bypassUTF` true (buffer + `ContentType` for the viewer).

- **`src/utils/file-utils.js`**
  - `encodeDocument(document, s3FileBuffer)`: builds `data:${fileType};base64,` from buffer using `document.file.file_type` (default `image/jpeg`).

- **`index.js`**
  - `app.use("/image", ImageViewerRouter)` → effective route `GET /image/view`.
