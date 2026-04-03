# Collaborate on document processing

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Collaborate on document processing |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (bookkeeping/accounting operators) |
| **Business Outcome** | Operators can prioritize work, route documents to the right people, apply bulk status and review actions, and pull accountants in via Slack when needed |
| **Entry Point / Surface** | Coding Engine operator UI (document list and detail); authenticated `document` API (`AuthGuard`) |
| **Short Description** | Exposes review-oriented document counts per user, directory of assignees from admin groups, bulk assign/unassign with per-user workload counters, bulk updates by action type (archive, delete, restore, status change, auto-publish review flags), and Slack escalation to accountant channels with company role context |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Sleek Back (`/admin/users/admins` for assignees; company resource users for Slack routing); Slack notifications API (`SLEEK_SLACK_BASE_URL` `/event/message-accountant-channel`); Sleek Auditor log ingestion; Kafka/document event publishing (`eventUtils.publishEvent`); user activity (`doc_count` maintenance on assign/unassign) |
| **Service / Repository** | `acct-coding-engine` (`document.controller.ts`, `document.service.ts`); `sleek-back` (HTTP); internal Slack notifications service |
| **DB - Collections** | `documentdetailevents` (documents; `assignee_user`, action flags such as `is_archived`, `is_deleted`, `is_auto_flow_reviewed`, `is_auto_reconcile_reviewed`, status updates); `useractivities` (per-user `doc_count` read for counts endpoint and updated on assignment changes) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `GET /document/counts` is described in Swagger as “to review” counts but implementation returns `userActivity.doc_count` from user activity — confirm intended semantics vs UI. Exact product navigation label for the operator document workspace. Whether all markets use the same Slack channel mapping (`ACCOUNT_MANAGERS_CHANNELS`) |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `document.controller.ts` (auth: `AuthGuard` unless noted)

- `GET /document/counts` — `getDocCounts`; summary: “Get to review document counts”
- `PUT document/action/:action` — `updateFeedbackByActionType` / `updateDocumentByActionType`; summary: “Update Document By Action Type”
- `GET document/assignees` — `getAssignees` (passes `Authorization`, `app-origin` headers)
- `PUT document/assignees` — `updateDocumentAssignee`
- `POST document/askAccountant/:documentId` — `askAccountantByDocId`; summary: “To send slack message to accountant channels”

### `document.service.ts`

- **Counts:** `getDocCounts(userId)` → `userActivityService.getUserActivity(userId)` → returns `userActivity?.doc_count || 0` (not an aggregation on `documentdetailevents` in this path). Deprecated `getCountsForToReviewAndToReconcileDocs` still contains aggregation pipelines for to-review / to-reconcile style counts — not wired to `GET /counts` in the controller
- **Action types:** `updateDocumentByActionType` maps route `action` to `DocumentActionType` / `DocumentActionTypeVariable` (`archive`, `delete`, `change_status`, `restore`, `unarchive`, `review`, `review_auto_recon`), validates IDs and bulk status when `change_status`, updates via `documentModel.updateMany` / delete flows, publishes document events, calls `sleekAuditorService.insertLogsToSleekAuditor` for selected actions, and `userActivityUpdateForArchiveAndDeleteAction` where applicable
- **Assignees:** `getAssignees` calls `SLEEK_BACK_API_BASE_URL` + `/admin/users/admins` with `group_name` in `['Bookkeeping', 'Bookkeeping Admin', 'Accounting']`, merges unique users. `updateDocumentAssignee` sets or `$unset`s `assignee_user` on documents, `incrementBookkeeperDocCount` / `decrementBookkeeperDocCount`, `publishEvent` `DocumentEventType.BULK_UPDATED`, per-document Sleek Auditor logs
- **Slack:** `askAccountantByDocId` loads document by id, `sleekBackService.getAccountingCompanyResourceUsersWithRoleInfoFromSleekBack` and `getUserInfoFromSleekBack`, builds payload in `generateSlackMessagePayload` (bookkeeper, team leader, manager, portfolio lead roles; manager-specific Slack channel from `ACCOUNT_MANAGERS_CHANNELS`; document deep link via `SLEEK_CODING_ENGINE_UI_BASE_URL`), then `notifyAccountMangerChannel(payload)`

### External / shared utilities

- `notifyAccountMangerChannel` (`src/utils/generic.ts`) — POST to `${SLEEK_SLACK_BASE_URL}/event/message-accountant-channel` with `SLACK_NOTIFICATIONS_API_KEY`

### Enums

- `DocumentActionType` / `DocumentActionTypeVariable` in `document/enum/document.enum.ts` — action strings and Mongo field names for review flags and lifecycle flags
