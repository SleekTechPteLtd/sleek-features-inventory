# Manage company Zendesk tickets

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage company Zendesk tickets |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (Sleek Admin role) |
| **Business Outcome** | Internal teams can see and resolve Zendesk work in Sleek Admin in step with the live helpdesk, so support actions stay consistent with ticket status in Zendesk. |
| **Entry Point / Surface** | Sleek Admin (authenticated API) — `GET/POST /v2/zendesk/...` (see Evidence) |
| **Short Description** | Sleek Admin fetches a ticket by Zendesk ID, searches tickets for a company (optionally filtered by subject), and closes a ticket by ID. All calls go through the Sleek Zendesk integration service to Zendesk. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Depends on **Sleek Zendesk** HTTP service (`SLEEK_ZENDESK_BASE_URL`); company search uses Zendesk search with `companyId` and/or `subject` plus enforced `notification` tag. Related: CDD/KYC Zendesk ticket creation and `ZendeskTicketLogs` flows in the same controller module. |
| **Service / Repository** | `sleek-back`; external **Sleek Zendesk** service (Zendesk API proxy) |
| **DB - Collections** | None for get-by-id, company search, or close-by-id paths (Zendesk-only). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact Sleek Admin UI navigation labels for these endpoints; whether any market restricts Zendesk usage. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Router mount:** `app-router.js` mounts this controller at `/v2/zendesk`.
- **`controllers-v2/zendesk-controller.js`**
  - Guards: `userService.authMiddleware` and `accessControlService.isIn("Sleek Admin")` on all routes.
  - **GET** `/tickets/company/:companyId` → `getCompanyZendeskTicketsHandler` — optional `subject` query (`req.query.subject`), company `companyId` from params or `req.query.companyId`; calls `getCompanyZendeskTickets({ subject, companyId })`.
  - **GET** `/ticket/:ticketId` → `getZendeskTicketById` → `getFormattedZendeskTicketById(ticketId)`.
  - **POST** `/ticket/:ticketId/close` → `closeZendeskTicketById` → `sleekZendeskService.closeTicket(ticketId)`.
- **`services/zendesk-service/zendesk-ticket-service.js`**
  - `getFormattedZendeskTicketById` → `sleekZendeskService.getTicketById(ticketId)` then `formatZendeskTicket` (ticket id, status, agent URL, assignee, created date).
  - `getCompanyZendeskTickets` → ensures `notification` tag is included, then `sleekZendeskService.searchTickets({ subject, companyId, tags })`; maps results with `formatZendeskTicket`.
- **`services/zendesk-service/sleek-zendesk-service.js`**
  - `getTicketById` GET `${SLEEK_ZENDESK_BASE_URL}/zendesk/tickets/:ticketId`.
  - `searchTickets` builds Zendesk query (`type:ticket`, subject and/or company id, `tags:` parts) GET `/zendesk/search?query=...`.
  - `closeTicket` POST `{base}/zendesk/tickets/:ticketId/close`.
