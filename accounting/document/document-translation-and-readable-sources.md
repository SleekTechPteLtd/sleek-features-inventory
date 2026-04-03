# Document translation and readable sources

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Document translation and readable sources |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User, Bookkeeper |
| **Business Outcome** | Users can detect the language of uploaded documents, obtain machine-translated copies for review, and open the original or translated file in the viewer with a readable payload for the PDF UI. |
| **Entry Point / Surface** | Sleek bookkeeping / customer app via document APIs (`/document/*`); exact screen labels not defined in this repo |
| **Short Description** | Authenticated users call language detection and translation endpoints that run Google Cloud Translation on files staged from S3 via GCS, persist `detected_language_code` and `translated_file_uri` on the document, and emit document update events. A separate endpoint returns a base64-encoded readable source for the original or translated S3 object for in-app viewing. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Google Cloud Translation and Cloud Storage; AWS S3 for source and translated file storage; MongoDB `documentdetailevents`; `eventUtils.publishEvent` on successful detection/translation (`DocumentEventType.UPDATED`); downstream consumers of document events |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | documentdetailevents |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether all markets use the same translation stack and quotas; whether UI always passes `documentFileUri` consistent with stored `file_uri` (body-based routes). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **HTTP surface (all `AuthGuard`):**
  - `POST /document/:documentId/check-language` — `detectLanguage` → `DocumentService.detectLanguage` (body: `documentFileUri`).
  - `POST /document/:documentId/translate` — `documentTranslation` → `DocumentService.documentTranslationProcess` (body: `documentFileUri`, `languageCode`).
  - `GET /document/readable-src/:documentId?doc=translated` — `getDocumentReadableSrcById` → optional `doc` query selects `translated_file_uri` vs `file_uri`.
- **`document.service.ts`:**
  - `getS3Body` parses S3 URIs and loads file bodies from S3.
  - `detectLanguage`: `googleCloudService.detectLanguage` on S3 body; `findByIdAndUpdate` sets `detected_language_code`; publishes `DocumentEventType.UPDATED` with `EventCaller.DOCUMENT_SERVICE.detectLanguage`.
  - `documentTranslationProcess`: S3 → `saveFileToGS` / `getGCSLinks`; `googleCloudService.translateDocument`; writes translated bytes back via `saveFileToGS`; `s3Service.uploadFileOnS3`; `findByIdAndUpdate` sets `translated_file_uri`; publishes `UPDATED` with `EventCaller.DOCUMENT_SERVICE.documentTranslationProcess`.
  - `getDocumentReadableSrcById` / `getReadableSrc`: loads from S3, `encodeDocument` from `src/utils/file.ts` for viewer-ready payload.
- **`document.schema.ts`:** collection `documentdetailevents`; fields `translated_file_uri`, `detected_language_code`.
