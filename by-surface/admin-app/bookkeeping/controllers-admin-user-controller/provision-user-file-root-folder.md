# Provision user file root folder

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Provision user file root folder |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (admin API); System / product flows also call the same service on registration and profile paths (see Evidence) |
| **Business Outcome** | Every user has a dedicated root folder in the file store so personal uploads, documents, and downstream file workflows have a stable anchor. |
| **Entry Point / Surface** | **Admin repair / hydrate:** Sleek Admin API — `POST /admin/users/:userId/files/hydrate-root-folder` (`users` `full` and `files` `full`). **Automatic:** same logic invoked from auth/onboarding and user profile flows elsewhere in sleek-back (not only this route). |
| **Short Description** | Ensures a user’s `root_folder` exists: if already set, no-op; otherwise creates the root folder via the files microservice when enabled, or legacy in-app `File` documents, then persists `users.root_folder`. The admin route explicitly hydrates missing roots and writes an audit log. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Files:** `@sleek-sdk/sleek-files` (`ExternalFileService.createUserRootFolder`) when `MICROSERVICES.FILES` toggle is on; otherwise `legacy-services/file-service`. **Also calls `createUserRootFolder`:** `services/auth/helpers.js`, OAuth registration, `controllers/user-controller.js`, `internal-service/user-profile-controller`, `company-user-controller`, `company-secretary-controller`, `corporate-director-service` — shared hydration pattern, not exclusive to admin. **Audit:** `buildAuditLogV2` / `saveAuditLogV2` on the admin hydrate route only. |
| **Service / Repository** | sleek-back; external sleek-files service when microservice toggle enabled |
| **DB - Collections** | `users` (`root_folder` ref to `File`); `files` (legacy path: folder doc at `/users/:userId/` with `user`, ACL arrays `can_view` / `can_edit` / `can_manage`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/admin/user-controller.js`

- **`POST /admin/users/:userId/files/hydrate-root-folder`** — `userService.authMiddleware`, `accessControlService.can("users", "full")`, `accessControlService.can("files", "full")`. Loads `User` by `userId`; `ResourceNotFoundError` if missing. Calls `fileService.createUserRootFolder(user)`. On success: `buildAuditLogV2` with action `user.files.hydrate-root-folders`, tags including `user`, `user-files`, `hydrate-root-folders`; `saveAuditLogV2`; responds `200` with `{ message: "User root folder created" }`.

### `services/file-service.js`

- **`createUserRootFolder(user)`** — Early return if `user.root_folder` is non-empty (`lodash` `isEmpty`). If files microservice toggle enabled: `ExternalFileService.createUserRootFolder(user)`, then `User.updateOne({ _id }, { $set: { root_folder: userRootFolder._id } })`. Else delegates to `LegacyFileService.createUserRootFolder(user)`.

### `services/legacy-services/file-service.js`

- **`createUserRootFolder(user)`** — Validates user instance. If `root_folder` already set, returns user. Else `File.findOne({ local_path: `/users/${user._id}/` })` to reuse existing folder; otherwise `File.create` with `type: "folder"`, `local_path`, `name: "root"`, `children: []`, permissions for `user._id`, `user: user._id`. Then `User.updateOne` sets `root_folder` to the file `_id`.

### `schemas/user.js`

- **`root_folder`** — `ObjectId` ref `"File"`.
