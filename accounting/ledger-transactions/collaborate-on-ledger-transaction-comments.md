# Collaborate on ledger transaction comments

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Collaborate on ledger transaction comments |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Bookkeeper, Finance User, Customer (authenticated users via customer app or internal tools) |
| **Business Outcome** | Teams and customers exchange messages on bank ledger lines so missing or incorrect supporting documents get resolved with clear accountability and read awareness |
| **Entry Point / Surface** | Sleek App / Admin / Coding Engine flows that surface uncoded ledger transactions (`app-origin`: `admin`, `customer`, `coding-engine` on company-scoped list); REST `ledger-transactions` API (`/ledger-transactions`, comment sub-routes) |
| **Short Description** | Users post threaded comments on a ledger transaction; each comment stores source (Sleek vs customer from email domain), commenter, and per-user read state. APIs list comments with read flags, batch unread counts across transactions, filter lists by unread, and mark comments read so coordination stays visible without duplicate work |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Ledger transaction list and document upload flows (`document_upload_status`, `submit-document`); commenter display names from Sleek Back (`getUsersInfoFromSleekBack`); rejection and bulk update paths may append comments via service internals |
| **Service / Repository** | `acct-coding-engine` (`ledger-transaction.controller.ts`, `ledger-transaction.service.ts`); `sleek-back` (HTTP user lookup for commenter names) |
| **DB - Collections** | `ledger_transactions` (embedded `comments[]` with `date`, `comment`, `source`, `commenter_id`, `read_by[]`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether comment-only routes should enforce `CompanyAccessGuard` like the main company-scoped list (currently `AuthGuard` only on add/list/mark-read/batch unread). Exact product labels for ledger transaction screens per app |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `ledger-transaction.controller.ts` (`@Controller('ledger-transactions')`, `@ApiTags('ledger-transaction')`, `Authorization` security)

- `GET /ledger-transactions` — `getLedgerTransactionsForCompany`; `AuthGuard`, `CompanyAccessGuard`; optional `has_unread_comments` filter; returns `comments` (with `commenter_name`) and `unread_comments_count` per row
- `POST /ledger-transactions/comments/unread-counts` — `getBatchUnreadCounts`; `AuthGuard`; body `ledger_transaction_ids[]`
- `POST /ledger-transactions/:ledger_transaction_id/add-comment` — `addCommentToTransaction`; `AuthGuard`; body `{ comment }`
- `GET /ledger-transactions/:ledger_transaction_id/comments` — `getCommentsForTransaction`; `AuthGuard`; returns `comments` with `is_read`, `total_count`, `unread_count`
- `POST /ledger-transactions/:ledger_transaction_id/comments/mark-read` — `markCommentsAsRead`; `AuthGuard`; body `comment_ids[]`

### `ledger-transaction.service.ts`

- **Add comment:** `addCommentToTransaction` — validates non-empty and max 4000 chars; sets `CommentSource` to `SLEEK` if email domain contains `sleek`, else `CUSTOMER`; `$push` comment with `read_by` seeded to author; `findOneAndUpdate` on `ledger_transaction_id`
- **List comments:** `getCommentsForTransaction` — loads transaction; builds comment `id` as `${transaction._id}_${index}`; resolves names/initials via `sleekBackService.getUsersInfoFromSleekBack` (capped IDs); `is_read` when requesting user id is in `comment.read_by`
- **Mark read:** `markCommentsAsRead` — parses indices from comment id suffix after `_`; appends user to `read_by` when missing; `$set` full `comments` array
- **Batch unread:** `getBatchUnreadCounts` — `find` by `ledger_transaction_id` `$in`, counts comments where user not in `read_by`; missing ids yield `unread_count: 0`
- **List aggregation:** `unread_comments_count` computed in MongoDB aggregation from `comments` vs `read_by` for filtering and pagination (same service file)

### `models/ledger-transaction.schema.ts`

- `CommentSchema`: `date`, `comment`, `source` (`CommentSource`), `commenter_id`, `read_by` (ObjectId[])
- Parent: `@Schema({ collection: 'ledger_transactions', timestamps: true })` — comments embedded on `LedgerTransaction`

### `ledger-transaction.service.ts` (supporting)

- `fetchCommenterUserInfo` — batch commenter resolution for transaction lists via `sleekBackService.getUsersInfoFromSleekBack`, continues without names on external failure
