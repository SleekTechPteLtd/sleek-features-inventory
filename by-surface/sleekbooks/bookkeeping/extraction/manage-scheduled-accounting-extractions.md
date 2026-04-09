# Manage scheduled accounting extractions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage scheduled accounting extractions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators can define and maintain extraction jobs that pull accounting source data (Xero, Dext, or Hubdoc) for a chosen region and date range, with a clear guard so only one run is active at a time. |
| **Entry Point / Surface** | `sleek-erpnext-service` HTTP API under `@Controller('extraction')` (base path `/extraction`). No auth guards appear on these routes in this module; exact Sleek app or back-office navigation is not defined in this repo. |
| **Short Description** | Create extraction jobs with type (Xero, Dext, Hubdoc), cron-style `schedule`, region, optional start/end dates, and lifecycle status. List and fetch by id, update, and delete records. New creates are rejected with HTTP 429 when any job is already `inprogress`. Dates are normalised to start/end of day when saving. |
| **Variants / Markets** | `SG`, `HK`, `AU`, `UK` (schema enum; default `SG`). |
| **Dependencies / Related Flows** | Persists job metadata only in this slice; actual sync to Xero, Dext, or Hubdoc is not implemented in the reviewed files—downstream workers or other services likely consume `extractions` documents by status/schedule. Related: other accounting ingestion and document pipelines in the broader platform. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | `extractions` (Mongoose model `Extraction`; default pluralised collection name). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | No `SleekBackAuthGuard` or M2M guard on extraction routes—confirm whether this API is internal-only or needs hardening. `GET /extraction` passes `query` straight to `find(query)`—confirm expected filters and abuse controls. Controller body for create is typed as `Extraction` while service uses `CreateExtractionDto`; confirm validation behaviour in production. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/extraction/extraction.controller.ts`

- **`@ApiTags('extraction')`**, **`@Controller('extraction')`** — base path `/extraction`.
- **`POST /`** — `@ApiOperation({ summary: 'Create New Extraction' })`, `ValidationPipe`, body `Extraction` → `getRunningTask()`; if count is `0`, `create`, else `429` with message `Task is running, try again later!`.
- **`GET /`** — `@ApiOperation({ summary: 'Get All Extractions' })`, query → `readAll`.
- **`GET /:id`** — `@ApiOperation({ summary: 'Get One Extraction' })`, `readById`.
- **`PUT /:id`** — `update`.
- **`DELETE /:id`** — `delete`.

### `src/extraction/extraction.service.ts`

- **`@InjectModel(Extraction.name)`** — persistence via `extractionModel`.
- **`create`**: default `startDate` to `1970-01-01` or `moment(...).startOf('day')`; default `endDate` to end of today or `moment(...).endOf('day')`; `new extractionModel(...).save()`.
- **`readAll`**: `find(query)`.
- **`readById`**: `findById`.
- **`update`**: same date normalisation as create; `findByIdAndUpdate`.
- **`delete`**: `findByIdAndRemove`.
- **`getRunningTask`**: `find({ status: 'inprogress' }).count()`.

### `src/extraction/schemas/extraction.schema.ts`

- **`extractionType`**: required, enum `extractionTypes` (see enum file).
- **`schedule`**: required string (cron-style usage implied by field name, not validated in schema).
- **`startDate`**, **`endDate`**, **`completionDT`**: optional dates.
- **`status`**: enum `posted`, `inprogress`, `completed`, `failed`, `aborted`, `deleted`; default `posted`.
- **`region`**: enum `SG`, `HK`, `AU`, `UK`; default `SG`.
- **`timestamps: true`** — Mongoose `createdAt` / `updatedAt`.

### `src/extraction/enum/extractionType.enum.ts`

- **`extractionTypes`**: `xero`, `dext`, `hubdoc`.

### `src/extraction/extraction.module.ts`

- **`MongooseModule.forFeature([{ name: Extraction.name, schema: ExtractionSchema }])`** — registers model for DI.

### `src/extraction/dto/create-extraction.dto.ts`

- **`CreateExtractionDto`**: class-validator on `extractionType`, `schedule`, dates, `status` — aligned with create path typing in service; controller currently types body as `Extraction` instead of DTO.
