# Manage promotional coupons

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage promotional coupons |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin / operations staff with **Coupons** permission (`permissions.coupons === "full"` for create, edit, remove) |
| **Business Outcome** | Authorized staff can define and maintain promotional discount coupons (code, amount, usage cap, expiry, applicable services) so marketing can run incentives safely; referral-program coupons are hidden from this list so they are not managed here. |
| **Entry Point / Surface** | **sleek-website** admin: **Coupons** — React `AdminCouponsView` mounted on `#root` from `src/views/admin/coupons.js`. `AdminLayout` with `sidebarActiveMenuItemKey="coupons"`, drawer hidden. |
| **Short Description** | Paginated, sortable, filterable table of coupons (code, title, amount, usage vs max, created/expiry). **New Coupon** opens a form for code, title, negative amount, max usage, expiry date, and **applicable service** (select from `COUPON_APPLICABLE_SERVICES`). **Edit** / **Remove** are allowed only when coupon `status === "new"` and the user has full coupon permission. Rows with `type === "referral_program"` are filtered out client-side so they never appear. Persisted via main HTTP API under `/admin/coupons` (GET list, POST create, PUT update, DELETE). |
| **Variants / Markets** | **Unknown** from this UI (API host defaults to production `https://api.sleek.sg` vs local `http://localhost:3000`; no market flag in view). |
| **Dependencies / Related Flows** | **Main Sleek API** (`getBaseUrl()`): authenticated admin coupon CRUD on `/coupons` paths with `admin: true` → `/admin/coupons…`. **Session**: `getUser` → `GET /admin/users/me`; unverified users sent to `/verify/`. **Separate product surface**: newer **New Coupons** admin (`src/views/admin/new-coupons/create-edit.js`) uses **payment API** and richer fields — parallel capability. Customer **checkout** may use `lockCoupon` (`POST /coupons/lock`) elsewhere in `api.js` — not this screen. Referral coupons exist in the same backend dataset but are excluded in the UI filter. |
| **Service / Repository** | **sleek-website** (`coupons.js`, `api.js`, `constants.js`). **Main API** (coupon persistence — collection/schema not in this repo). |
| **DB - Collections** | **Unknown** (coupon records live in the main API backend; not visible from frontend files). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Long-term whether this legacy **Coupons** screen remains canonical vs **New Coupons** (`payment-api`); exact server-side schema and whether `referral_program` filtering should eventually be server-side; pagination uses `maxPage: response.data.length` which may not reflect total count across pages — **none** if acceptable as legacy behavior. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/coupons.js` (`AdminCouponsView`)

- **List**: `getCoupons({ query: { sortBy, sortOrder, code, title, skip, limit, amount }, admin: true })` then client filter `coupon.type !== "referral_program"`; optional `expiredAtFilter` further filters by formatted expiry date.
- **Permissions**: `user.permissions.coupons !== "full"` disables **New Coupon**, **Edit**, and **Remove**.
- **Mutations**: `createCoupon` / `updateCoupon` with JSON body `amount`, `code`, `title`, `expired_at`, `applicable_service` (string from select `.value`), `max_usage_nb`; `deleteCoupon(id, { admin: true })` with confirmation dialog.
- **Status gate**: Edit/delete disabled when `coupon.status` is set and not `"new"` (`couponStatusIsNotNew`).

### `src/utils/api.js`

- **Admin prefix**: `getResource` / `postResource` / `putResource` / `deleteResource` with `options.admin === true` rewrite base URL to `${getBaseUrl()}/admin` for the path segment (e.g. `/coupons` → admin routes on same host).
- **Coupons**: `getCoupons` → `GET ${getBaseUrl()}/coupons`; `createCoupon` → `POST` same; `updateCoupon(id)` → `PUT ${getBaseUrl()}/coupons/${id}`; `deleteCoupon(id)` → `DELETE` same. **`lockCoupon`** → `POST ${getBaseUrl()}/coupons/lock` (related checkout flow, not admin list).

### `src/utils/constants.js`

- **`COUPON_APPLICABLE_SERVICES`**: react-select options — `general`, `accountingPlan` (label Accounting), `corpSec` (label Corpsec).
- **`ADMIN_RESOURCES`**: registers **Coupons** resource with `sidebarMenuItemKeys: ["coupons"]`.
- **`NEW_COUPON_APPLICABLE_SERVICES`**: broader string list used by the newer new-coupons UI — not used by `coupons.js`.
