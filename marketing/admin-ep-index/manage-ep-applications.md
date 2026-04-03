# Manage EP applications

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage EP applications |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations user (Sleek admin / staff with Employment Pass admin access) |
| **Business Outcome** | Operations can see all Singapore Employment Pass (EP) applications with company and applicant context, seed new EP records for applicants, open the applicant-facing review flow, and install a browser bookmarklet to paste structured data into external forms. |
| **Entry Point / Surface** | **sleek-website** admin: **Employment Pass** (`/admin/ep/`) — `AdminLayout` with `sidebarActiveMenuItemKey="ep"`; primary actions “New EP” and “FormFill Tool”. Breadcrumb-style back when the inline “New EP” form is visible. |
| **Short Description** | Loads EP applications into a table (company name, applicant email, registered date, status, created date) and links each row to a **Review Form** URL on the public EP flow (`/ep/?epid=…&ar=1`). Staff can open an inline form to create or update an EP with company name and applicant email (create uses the admin API path). A dialog explains dragging the **Sleek FormFill** bookmarklet, which injects `bookmarklets/ep.js` from the current host for assisted browser entry. Unverified users are redirected to `/verify/`. |
| **Variants / Markets** | **SG** (Employment Pass is Singapore-specific). Other tenants: **Unknown** if this screen is hidden or unused. |
| **Dependencies / Related Flows** | **`api.getEps`** → **`GET ${base}/eps`** (no `admin` prefix in client). **`api.createEp`** with **`admin: true`** → **`POST ${base}/admin/eps`**. **`api.updateEp`** → **`PUT ${base}/eps/:id`** (update branch only if `epFormId` is set — not wired from list in this view). Public EP journey at **`/ep/`** for review (`ar=1`). Related admin screen: **`/admin/ep/edit`** (`src/views/admin/ep/edit.js`) for detailed read-only application/personal fields via **`getEp`**. Backend EP persistence and RBAC live in **sleek-back** (not in this repo). |
| **Service / Repository** | **sleek-website**: `src/views/admin/ep/index.js`, `src/utils/api.js` (`getUser`, `getEps`, `createEp`, `updateEp`). **sleek-back**: EP REST handlers and data store for `/eps` and `/admin/eps`. |
| **DB - Collections** | **Unknown** (backend). EP application documents and user linkage are not defined in sleek-website; expect a dedicated EP/application collection and `User` references in sleek-back. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether **`GET /eps`** without `/admin` is intentional for this page (vs **`GET /admin/eps`**) and how server-side scoping differs for admin sessions. Whether **`epFormId`** / update path is used from another entry or is legacy. Exact RBAC for EP admin menu items. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/ep/index.js` (`AdminEpView`)

- **Mount**: `domready` → `#root`; **`getUser`** then **`getEps`** in `componentDidMount`.
- **Layout**: `AdminLayout` with **`hideDrawer={true}`**, **`sidebarActiveMenuItemKey="ep"`**.
- **Toolbar**: **“New EP”** → `handleClickNew` sets `epFormVisible: true`, empty `formValues`. **“FormFill Tool”** → `handleClickFormFillTool` opens alert with instructions and draggable **`AnchorButton`** with `href` set to a `javascript:` bookmarklet that appends a script from **`${protocol}//${host}/bookmarklets/ep.js`**.
- **List** (`renderEps`): Table columns — index, **`ep.data.company_name`**, **`ep.user.email`**, **`ep.user.registered_at`** (formatted), **`ep.status`** (`startCase`), **`ep.createdAt`**. **Review Form** → **`AnchorButton`** to **`/ep/?epid=${ep._id}&ar=1`**, `target="_blank"`.
- **Empty state**: `NonIdealState` when `eps` empty.
- **Create/update form** (`renderEpForm`): Company name + applicant email; submit **`handleFormSubmit`** posts JSON `{ company_name, email }`. **`createEp({ body, admin: true })`** or **`updateEp(epFormId, { body })`**; on success **`getEps`**, hide form. Coupon-related disable logic references `formValues.coupon_status` (likely shared with other flows).
- **Auth**: **`getUser`** — if no `registered_at`, redirect **`/verify/`**; errors via **`checkResponseIfAuthorized`**.

### `src/utils/api.js`

- **`getEps`**: **`GET`** `` `${getBaseUrl()}/eps` `` via **`getResource`** — **no** `options.admin` rewrite → **`GET /eps`**.
- **`createEp`**: **`POST`** `` `${getBaseUrl()}/eps` `` via **`postResource`**; with **`admin: true`** → path becomes **`/admin/eps`**.
- **`updateEp`**: **`PUT`** `` `${getBaseUrl()}/eps/${epId}` `` via **`putResource`**; admin rewrite only if caller passes **`admin: true`** (index does not for update).
- **`getEp` / `submitEp`**: defined for EP detail and submit flows; used elsewhere (e.g. edit view), not in `index.js`.

### Static bookmarklet asset

- **`src/bookmarklets/ep.js`** (and **`ep.css`**) — loaded by the bookmarklet URL referenced from the FormFill dialog.

### Navigation (sidebar)

- **`src/components/admin-side-menu.js`**, **`src/components/new-admin-side-menu.js`**, **`src/components/mobile-admin-user-menu.js`** — link **`/admin/ep/`**, label **Employment Pass** (mobile).

### Backend (cross-repo)

- EP list/create/update semantics, MongoDB collections, and permission checks for **`/eps`** vs **`/admin/eps`** are implemented in **sleek-back**, not evidenced in this repository.
