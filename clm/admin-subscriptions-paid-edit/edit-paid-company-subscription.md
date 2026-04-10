# Edit Paid Company Subscription

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Edit Paid Company Subscription |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Allows admins to correct or update the terms of a company's paid subscription (service type, start date, duration) and review the associated invoices without leaving the admin panel. |
| **Entry Point / Surface** | Sleek Admin > Subscriptions > Paid Subscriptions > Edit |
| **Short Description** | Admin-only form that loads an existing company service record and allows updating its service type (Secretary, Director, Mailroom), start date, and duration in months. Associated invoices are displayed read-only for reference. On save, calls PUT /company-services/:id with admin privileges and redirects back to the paid subscriptions list. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Paid Subscriptions List (`/admin/subscriptions/paid/`); `GET /company-services/:id` (fetch); `PUT /company-services/:id` (update); `GET /companies` (company lookup); invoice records linked to the company service |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which backend repo handles `PUT /company-services/:id`? What DB collections (company_services, invoices) are touched server-side? Are market variants (SG/HK/UK/AU) differentiated at the service type level? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `views/admin/subscriptions/paid/edit/index.js` — React component `ServicesEdit`
- Admin layout with sidebar key `subscriptions` / `paid-subscriptions`
- URL param `?id=<companyServiceId>` identifies the record to edit

### API calls (via `src/utils/api.js`)
| Call | Endpoint | Purpose |
|---|---|---|
| `getCompanyService(id, { admin: true })` | `GET /company-services/:id` | Populate form with current values |
| `getCompanyies()` | `GET /companies` | Company list (unused in edit mode — company selector hidden when `formType !== "new"`) |
| `updateCompanyService(id, { admin: true, body })` | `PUT /company-services/:id` | Persist edits |

### Editable fields (form-segment-service.js)
- **service** — select: `secretary`, `director`, `mailroom`
- **start_at** — date picker (DD/MM/YYYY)
- **duration** — number input (months)

### Read-only invoice display (form-segment-invoice.js)
Each invoice attached to the company service is rendered disabled with:
- title, url, transaction_id, number, total_amount
- status: `processing` | `done` | `failed`

### Payload sent on submit
```json
{ "company_id": "...", "service": "...", "duration": 12, "start_at": "..." }
```

### Post-submit behaviour
Success → alert "Paid company subscription has been updated." → redirect to `/admin/subscriptions/paid/`
Error → alert with error message from API response.
