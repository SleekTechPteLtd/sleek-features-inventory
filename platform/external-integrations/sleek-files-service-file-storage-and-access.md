# Sleek Files Service (`sleek-files-service`) — file storage and access layer

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Shared file storage API (upload/download, folders, permissions, internal service endpoints) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer/admin applications via user-auth APIs; internal backend services via server-auth APIs |
| **Business Outcome** | Centralized and auditable file handling across products with consistent auth, permission checks, and cloud storage behavior |
| **Entry Point / Surface** | Public API routes under `/api/files` and `/api/folders`; internal routes under `/api/internal`; service health at `/api/health` |
| **Short Description** | `sleek-files-service` is a Node/TypeScript file platform service exposing user-authenticated file and folder operations (list, upload, download, move, rename, archive), plus server-authenticated internal endpoints for cross-service workflows. It persists metadata in MongoDB, stores file bytes in AWS S3 (encrypted and public buckets), applies PBAC-aware checks for file access paths, and provides health/build version endpoints for operations. |
| **Variants / Markets** | PBAC token-based permission path (`pbac_authorization`) when enabled; encrypted vs public S3 bucket flows; environment-dependent Sentry/Swagger behavior |
| **Dependencies / Related Flows** | Upstream auth/token verification (`user-auth` gateway, internal auth secret); shared SDK config (`@sleek-sdk/common` / `@sleek-sdk/sleek-platform`); apps that consume `/api/files` (for example `customer-mfe`, legacy backends) |
| **Service / Repository** | `sleek-files-service` (Bitbucket `sleek-corp/sleek-files-service`) |
| **DB - Collections** | MongoDB (file metadata/permissions/read status); S3 buckets for file binaries |
| **Evidence Source** | Codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Primary producer/consumer systems by environment; migration plan for legacy file endpoints in `sleek-back` |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-files-service

- `src/core/routers/api-router.ts` - route mounts: `/files`, `/folders`, `/internal` plus exported `healthRouter`.
- `src/modules/file/routers/file-router.ts` - user-auth endpoints: find/list/details/download/upload/move/rename/delete, zip-and-download, mark-as, upload profile pic.
- `src/modules/file/routers/folder-router.ts` - user-auth folder create/view.
- `src/modules/file/routers/internal-file-router.ts` - server-auth internal operations: db command, folder/file create/remove/find, reconcile, transfer-rights, internal upload/download/archive.
- `src/core/middlewares/user-auth-middleware.ts` - bearer auth -> user lookup and request context.
- `src/core/middlewares/server-auth-middleware.ts` - Basic internal auth with shared secret.
- `src/modules/file/services/file-service.ts` - core file lifecycle logic, metadata operations, and PBAC integration.
- `src/modules/file/services/remote-storage-service.ts` - remote file upload/download via S3 and CDN URL handling.
- `src/modules/file/services/pbac-service.ts` - PBAC token verification and permission checks by file local path.
- `src/gateways/aws/s3/aws-s3-gateway.ts` - AWS S3 adapters for encrypted/public bucket storage.
- `src/modules/health/health-router.ts` - service health/version endpoint.
- `src/server.ts` - Express app wiring (`/api`, `/api/health`) with logging, security middlewares, and request tracing.
- `package.json` - dependencies (`aws-sdk`, `mongoose`, `multer`, `@sleek-sdk/sleek-files`, `@sleek-sdk/sleek-platform`) and test/coverage scripts.

## Related

- [sleek-cms-sdk-and-platform-config.md](./sleek-cms-sdk-and-platform-config.md)
- [../operations/README.md](../operations/README.md)
