# Manage marketing coupons

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage marketing coupons |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin / operations staff with **Coupons** permission (`permissions.coupons === "full"` for **New Coupon**, **Edit**, and **Remove**) |
| **Business Outcome** | Authorized operators can oversee promotional coupons backed by the payment service—listing, comparing usage to caps, and removing or editing only while coupons are still in **new** status—so incentives stay controlled and aligned with service groups and expiry. |
| **Entry Point / Surface** | **sleek-website** admin: sidebar **Coupons** (`key="new-coupons"`, `href="/admin/new-coupons/"`) when `new_coupon.enabled` is true and **sleek billings** is not the active mode (`new-admin-side-menu.js`). React `AdminNewCouponsView` mounts from `src/views/admin/new-coupons/index.js` on `#root` with `AdminLayout`, `sidebarActiveMenuItemKey="new-coupons"`, drawer hidden. |
| **Short Description** | Paginated table of coupons (default server filter `type: "coupon"`) with sortable columns (code, title, calculation type, amount, current usage, created, expiry) and per-column filters (regex on code/title, select for calculation type and applicable service groups). **Current usage** is loaded per row via usages API and shown against **maxUsage**. **New Coupon** / **Edit** / **Remove** require full coupon permission; **Edit** and **Remove** are disabled unless `status === "new"`. **Remove** calls delete on the payment API; **New** / **Edit** navigate to `/admin/new-coupons/create-edit` (optional `?couponId=`). |
| **Variants / Markets** | Production payment API host `https://payment-api.sleek.sg` implies **SG**-oriented deployment; no explicit market dimension in the view—**Unknown** for multi-market behavior. |
| **Dependencies / Related Flows** | **Payment API** (HTTP): list `GET /coupons`, usages `GET /coupons/:id/usages`, delete `DELETE /coupons/:id`; create/update live on same service (`createCoupon` / `updateCoupon` in `payment-api.js`, used from create-edit flow). **Session**: `api.getUser()` → unverified users redirected to `/verify/`. **Platform config**: `getPlatformConfig()` for currency symbol in the UI. **Legacy parallel UI**: older **Coupons** screen (`src/views/admin/coupons.js`, main API) documented separately—different backend and fields. **Constants**: `NEW_COUPON_APPLICABLE_SERVICES` for filter options on applicable service groups. |
| **Service / Repository** | **sleek-website** (`views/admin/new-coupons/index.js`, `utils/payment-api.js`). **payment-api** service (external HTTP backend for coupon persistence and usages). |
| **DB - Collections** | **Unknown** from this codebase (storage owned by payment-api; not referenced in frontend). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Coexistence and operator guidance between **New Coupons** (payment-api) and legacy **Coupons** (main API); whether usages totals can diverge from list sort field `currentUsage`; exact payment-api data model—**none** if out of scope for frontend inventory. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/new-coupons/index.js` (`AdminNewCouponsView`)

- **List**: `paymentApi.getCouponList({ query: { sort: JSON string, filter: JSON string (includes `type: "coupon"` and optional `$regex` filters), limit, page } })` → `GET` payment service `/coupons`.
- **Usage column**: after each list response, `fetchCouponUsage(couponId)` → `paymentApi.getCouponUsages(couponId)`; uses `usage.data.totalDocs` merged into `couponUsages[coupon._id]`, displayed as `{usage}/{coupon.maxUsage}`; falls back to `0` on error.
- **Sort**: `handleClickTableHeader` toggles per-field sort (e.g. `code`, `title`, `calculationType`, `amount`, `currentUsage`, `createdAt`, `expiredAt`) and refetches.
- **Filter**: `handleChangeFilter` merges `$regex` / `$options: "i"` into `filter`, resets page to 1, debounced refetch.
- **Pagination**: toolbar prev/next and direct page input update `response.page` and refetch.
- **Permissions**: `user.permissions.coupons !== "full"` disables **New Coupon**, **Edit**, **Remove**.
- **Status gate**: `couponStatusIsNotNew` when `status` exists and is not `"new"`—disables **Edit** and **Remove**.
- **Delete**: confirmation dialog → `paymentApi.deleteCoupon(couponId)` → refresh list.
- **Navigation**: `handleClickNewCoupon` → `/admin/new-coupons/create-edit`; `handleClickEditCoupon` → `/admin/new-coupons/create-edit/?couponId=…`.

### `src/utils/payment-api.js`

- **Base URL**: `PAYMENT_API` env, else production `https://payment-api.sleek.sg`, else `http://localhost:3020`.
- **Coupons**: `getCouponList` → `GET ${base}/coupons`; `getCouponDetail` → `GET ${base}/coupons/${id}`; `getCouponUsages` → `GET ${base}/coupons/${id}/usages`; `deleteCoupon` → `DELETE ${base}/coupons/${id}`; `createCoupon` / `updateCoupon` → `POST` / `PUT` `${base}/coupons` and `${base}/coupons/${couponId}` (create-edit screen).
- **Auth**: responses pass through `checkResponseIfAuthorized` / `getDefaultHeaders` like other API helpers.

### `src/components/new-admin-side-menu.js`

- **Coupons** menu item for the new flow: `new_coupon.enabled && !sleekBillingsEnabled`, `href="/admin/new-coupons/"`, `key="new-coupons"`.

### `src/utils/constants.js`

- **`NEW_COUPON_APPLICABLE_SERVICES`**: options for applicable service group filter column (imported in `index.js`).
