# Comment on Company Subscription Record

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Comment on company subscription record |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Admin team members can maintain a running communication log on a company's account directly from the subscription list, enabling coordinated subscription management without switching context. |
| **Entry Point / Surface** | Sleek Admin > Subscriptions (New) > Comment icon per subscription row |
| **Short Description** | Each row in the admin subscriptions table exposes a comment icon that opens a popover with a paginated threaded comment list scoped to the company. Admins can post new comments and load historical ones in pages of 20. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | sleek-auditor API (`/v2/sleek-auditor/api/log/company/{companyId}/comment/`); admin subscriptions list view; company audit log |
| **Service / Repository** | sleek-website (frontend), sleek-auditor (backend API) |
| **DB - Collections** | Unknown — stored via sleek-auditor service; collection not visible in this repo |
| **Evidence Source** | codebase |
| **Criticality** | Low |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which backend repo owns the sleek-auditor `/v2/sleek-auditor/api/log/company/{companyId}/comment/` endpoint and what collection it writes to? Are comments visible anywhere outside this admin subscriptions table (e.g. company detail page)? Is there any role-based access control beyond being logged in as an admin? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/views/admin/subscriptions/new/components/table.js` — `SubscriptionsTable` React component; contains `popoverOpen`, `popoverClose`, `loadCommentsAndHistory`, `handleLoadMoreComments`, `handlePostComment` methods
- `src/utils/api-sleek-auditor.js` — `getCompanyComments` and `postCompanyComment` functions

### API calls
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/v2/sleek-auditor/api/log/company/{companyId}/comment/` | Fetch paginated comments for a company (query param `skip` for pagination, page size 20) |
| PUT | `/v2/sleek-auditor/api/log/company/{companyId}/comment/` | Post a new comment for a company |

### Comment payload (POST)
```json
{
  "entry_type": "comment",
  "actionBy": { "_id", "first_name", "last_name", "email" },
  "company":  { "_id", "name", "uen" },
  "text": "<comment body>"
}
```

### UI behaviour
- Comment icon (`CommentIcon`) rendered in a dedicated column of every subscription row
- Clicking the icon fetches the first 20 comments and opens a `MUIPopover` anchored to the icon
- Comments displayed as a scrollable `List` with author name, body, and formatted timestamp (`moment`)
- "Load More" link appears when 20 or more comments are returned; each click advances `skip` by 20 and appends results
- Text input with multiline `TextField`; empty submission is blocked client-side with an error helper text
- After a successful post the list is re-fetched from page 0 and scrolled to the top
- A `window.dispatchEvent(new CustomEvent('resize'))` is fired post-post as a workaround to resize the popover
