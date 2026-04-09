# Record user activity for bookkeeping operations

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Record user activity for bookkeeping operations |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Bookkeeper, Finance User, Operations User, System |
| **Business Outcome** | Bookkeeping teams keep an accurate picture of who is active, in what role, and how many documents they hold in the review pipeline so presence and per-bookkeeper workload limits stay enforceable. |
| **Entry Point / Surface** | Sleek Bookkeeping flows that emit activity (documents, suppliers, sessions); API surface `POST user-activity` on acct-coding-engine; internal calls from document and supplier services |
| **Short Description** | Upserts per-user activity records (identity, role, last activity, document count and reset time). When `last_activity` is login or logout, the service recounts documents assigned to the user in “to review” pipeline statuses for active companies and refreshes `doc_count` and `doc_count_resetAt`. Other modules increment or decrement counts and pick the least-loaded recently active bookkeeper using config-driven limits. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Documents** (`documentdetailevents`, assignee and status) for pipeline counts and many `createOrUpdateUserActivity` calls; **supplier** flows for activity updates; **claim-report**, **feedback**, **ledger-transaction**, **reconciliation-manual** modules register `UserActivityService`; bookkeeper selection via `findRecentlyActiveBookkeeperWithLeastDocCount` using `BK_ACTIVE_PERIOD`, `BK_MAX_DOC`, `BK_DOC_RESET_PERIOD` |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `useractivities` (UserActivity, CODING_ENGINE); `documentdetailevents` (Document, SLEEK_RECEIPTS) for counts; `companies` (Company, CODING_ENGINE) for active receipt-system companies scoped in `resetDocCount` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `LastActivity` in `user-activity.interface.ts` does not list `logout`, but `createOrUpdateUserActivity` treats `logout` like `login` for doc recount—confirm whether typings should include `logout` and whether `POST user-activity` is authenticated at gateway or intentionally open. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/user-activity/user-activity.controller.ts`

- **HTTP**: `POST user-activity` → `createOrUpdate` with `UpdateOrCreateUserActivityDto` body; `@ApiOperation` summary “To create or update user activity”.
- **Guards**: No route-level guards on the controller (rely on platform/gateway or internal use—verify deployment policy).

### `src/user-activity/user-activity.service.ts`

- **Upsert**: `createOrUpdateUserActivity` — `findOne` by `user_id`, merge, `findOneAndUpdate` with `$set` on `user_id`, `email`, `user_role`, `last_activity`, `doc_count`, `doc_count_resetAt`, `{ upsert: true, new: true }`.
- **Login/logout recount**: If `last_activity` is `login` or `logout`, returns `resetDocCount(userId)` instead of the bare upsert result.
- **`resetDocCount`**: Loads active companies (`receipt_system_status: 'active'`), counts documents where `assignee_user` matches, status in `PROCESSING`, `EXTRACTING`, `ERROR`, `PUBLISHING`, with non-archived / non-deleted / non-duplicate filters and optional `company` filter; updates `doc_count` and `doc_count_resetAt`.
- **Workload helpers**: `incrementBookkeeperDocCount` / `decrementBookkeeperDocCount` adjust `doc_count` with `$inc`, or call `resetDocCount` when limits or time window (`BK_DOC_RESET_PERIOD`) warrant; `findRecentlyActiveBookkeeperWithLeastDocCount` sorts by lowest `doc_count` among recent `updatedAt` bookkeepers under `BK_MAX_DOC`; `findDefaultBookkeeper` by email; `getUserActivity` by `user_id`.

### `src/user-activity/dto/updateOrCreateUserActivityDTO.ts`

- Validated fields: required `user_id`; optional `email`, `user_role`, `last_activity`, `doc_count`, `doc_count_resetAt`.

### `src/user-activity/models/user-activity.schema.ts`

- Mongoose schema with `timestamps: true`; fields align with DTO; default collection name `useractivities` (no explicit `collection` option).

### `src/user-activity/interface/user-activity.interface.ts`

- **`UserRole`**: `bookkeeper`, `bookkeeper_admin`, `accountant`, `accountant_admin`, `super_admin`, `it_support`.
- **`LastActivity`**: includes `login`, document/supplier-focused values; see open question on `logout`.

### `src/user-activity/user-activity.module.ts`

- Registers models on `DBConnectionName.CODING_ENGINE` (UserActivity, Company) and `DBConnectionName.SLEEK_RECEIPTS` (Document) for cross-DB doc counting.
