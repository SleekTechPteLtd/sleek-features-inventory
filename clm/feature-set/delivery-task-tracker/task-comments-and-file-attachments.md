# Document Task Progress with Comments and File Attachments

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Document Task Progress with Comments and File Attachments |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (internal delivery team member) |
| **Business Outcome** | Enables delivery team members to document task progress, attach proof-of-completion files, and maintain a full audit trail of task lifecycle events for accountability and client delivery transparency. |
| **Entry Point / Surface** | Sleek Service Delivery API > task-activities endpoints (admin-only, internal tooling) |
| **Short Description** | Team members post text comments, link references, and file attachments (up to 10 files per upload) against a delivery task. All activity — including status changes, assignments, due-date edits, and deletions — is stored as a typed audit log per task. Files are stored in S3 and accessed via time-limited presigned URLs. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Tasks module (`tasks` table, Task entity); FileUploadService (S3 object storage, path prefix `task-activities/{taskId}/`); User & Company entities; delivery task assignment flow (bulk ASSIGNMENT activities created via `bulkCreateAssignmentActivities`); deliverables and subscription relations (loaded in paginated queries) |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | `task_activities` (primary), `tasks`, `users`, `companies` (via joins/relations); `deliverables`, `subscriptions` (via nested joins in findAll) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | No client-facing surface identified in code — confirm whether delivery portal exposes activity feed to clients or only internal staff. Presigned URL TTL defaults to 3600 s; confirm if this is appropriate for proof-of-completion downloads. `AutoMarkReason` enum referenced on entity — unclear how system-driven status changes interact with manual activity logging. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `task-activities/controllers/task-activities.controller.ts`
- Guard: `@SleekBackAuth('admin')` on entire controller — admin-scoped internal API only.
- `POST /task-activities` — create a single activity (comment, status change, assignment, etc.) via `CreateTaskActivityDto`.
- `POST /task-activities/upload` — multipart upload accepting up to 10 files (`FilesInterceptor('files', 10)`). Each file becomes a separate `TaskActivity` record typed `FILE`; if text content is provided it is attached to the first file only as `COMMENT_AND_FILE`.
  - Files stored to S3 via `FileUploadService.uploadFile()` at path `task-activities/{taskId}/{timestampedFileName}`.
  - Filenames sanitised (Unicode normalisation, strip problematic chars) and timestamped to avoid S3 key collisions.
- `GET /task-activities` — paginated list with filters: `taskId`, `companyId`, `activityType`, `activityTypes[]`, `performedByUserId`, `includeDeleted`.
- `GET /task-activities/task/:taskId` — paginated activity feed for a single task (default limit 50).
- `GET /task-activities/:id/file-url` — returns a presigned S3 URL (`FileUploadService.getPublicUrl`) for file-type activities; TTL defaults to 3600 s.
- `PATCH /task-activities/:id` — edit activity content.
- `DELETE /task-activities/:id` — soft-delete: sets `recordStatus = DELETED` on the original record **and** creates a new deletion-log activity (`COMMENT_DELETED`, `LINK_DELETED`, or `FILE_DELETED`) to preserve the audit trail.

### Service — `task-activities/services/task-activities.service.ts`
- `create()`: looks up the parent task to denormalise `companyId` onto the activity record.
- `bulkCreateAssignmentActivities()`: batch-inserts `ASSIGNMENT` activities for multiple tasks in a single save — called from bulk role-assignment flows.
- `findAll()` query builder: left-joins `performedByUser`, `assignedToUser`, `task`, `deliverable`, `subscription` for rich response payloads.
- `remove()`: soft-delete pattern — original record marked DELETED, deletion-log activity inserted; only COMMENT, LINK, FILE, and COMMENT_AND_FILE types generate a deletion log (ASSIGNMENT / STATUS_CHANGE / etc. do not).
- Uses TypeORM `Repository<TaskActivity>` — PostgreSQL (not MongoDB).

### Entity — `task-activities/entities/task-activity.entity.ts`
- Table: `task_activities`
- `TaskActivityType` enum values: `COMMENT`, `LINK`, `FILE`, `COMMENT_AND_FILE`, `ASSIGNMENT`, `STATUS_CHANGE`, `DUE_DATE_CHANGE`, `COMPLETED_DATE_CHANGE`, `COMMENT_DELETED`, `LINK_DELETED`, `FILE_DELETED`
- File fields: `fileName`, `fileKey` (S3 object key), `fileMimeType`, `fileSize`
- Link fields: `linkUrl`, `linkTitle`
- Status change fields: `previousStatus`, `newStatus`, `autoMarkReason`
- Relations: `task` (CASCADE delete), `company` (CASCADE delete), `performedByUser` (SET NULL), `assignedToUser` (SET NULL)
- `companyId` is indexed and denormalised from the parent task for efficient company-scoped queries.
