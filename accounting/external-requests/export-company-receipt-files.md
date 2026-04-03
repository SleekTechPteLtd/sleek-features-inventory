# Export company receipt files

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Export company receipt files |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, System (integrations calling the external receipts API) |
| **Business Outcome** | Operators or connected systems can download all stored receipt files for a client company in a single ZIP for support, audit handoff, or downstream processing without pulling each object manually from storage. |
| **Entry Point / Surface** | Sleek Receipts service — External API base `/api/external` — `GET /receipts/:company_id` returns `files.zip`. Not defined as an end-user app screen in this repo; consumed by tools or integrations that can reach the service. |
| **Short Description** | For a valid MongoDB `company_id`, loads all `DocumentDetailEvent` rows for that company, builds a ZIP with `archiver`, and streams it to the client. Each included file is fetched from S3 using the document’s `file_uri`: the uploader generates a short-lived signed GET URL, the handler downloads the bytes with HTTP, and appends them under the object key’s basename. Returns 404 if no documents exist for the company; 400 for invalid id format. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** Receipt documents must exist with `file_uri` (e.g. `s3://bucket/key`) populated when files were stored via S3 upload paths in `FileUploader`. **Storage:** AWS S3 signed URLs (`getObject`, default expiry 500s in `generateSignedUrl`). **Downstream:** Any workflow that needs a bulk export of originals per company. Documents that only have `file_url` and no `file_uri` are not added to the archive (query selects both fields but the loop only processes `file_uri`). |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `documentdetailevents` (Mongoose model `DocumentDetailEvent`); read on `company` match, fields `file_url`, `file_uri` |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether `/api/external` routes are protected by auth, API gateway, or private network only is not defined in the reviewed files. Whether callers expect `file_url`-only documents to appear and should be handled differently. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`index.js`**: Mounts `ExternalRequestsRouter` at `/api/external`, so the export route is **`GET /api/external/receipts/:company_id`**.
- **`src/routes/external-requests.js`**: `router.get("/receipts/:company_id", …)` — validates `company_id` with `mongoose.Types.ObjectId.isValid` (400 on failure). `DocumentDetailEvent.find({ company: company_id }).select('file_url file_uri')`; 404 when `!queryResults.length`. Uses `archiver` (`zip`, zlib level 9), `res.attachment('files.zip')`, `archive.pipe(res)`. For each document, only if `doc.file_uri`: `FileUploader.generateSignedUrl(doc.file_uri)` then `axios.get(signedUrl, { responseType: 'arraybuffer' })`, `archive.append(response.data, { name: doc.file_uri.split('/').pop() })`. `archive.finalize()`. Generic 500 on errors.
- **`src/files/uploader.js`**: `FileUploader` singleton; `generateSignedUrl(file_uri, expirySeconds = 500)` strips `s3://`, splits bucket vs key, calls `s3.getSignedUrl('getObject', …)`. Upload paths elsewhere set `fileUri` as `s3://${Bucket}/${Key}`.
- **`src/schemas/document-detail-event.js`**: `company` (ObjectId, required), `file_url`, `file_uri` (strings), plus other document fields not used by this route.
