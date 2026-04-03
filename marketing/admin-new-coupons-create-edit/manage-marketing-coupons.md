# Manage marketing coupons

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage marketing coupons |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Marketing or admin operators (authenticated Sleek admin session) |
| **Business Outcome** | Staff can create and maintain promotional coupon codes with discount rules, limits, and service scoping so valid offers can be applied during customer checkout and billing. |
| **Entry Point / Surface** | **sleek-website** admin: **New Coupons** — React view `AdminCouponsCreateEditView` on `#root` from `src/views/admin/new-coupons/create-edit.js`. Sidebar active key `new-coupons`. List/back: `/admin/new-coupons`; create/edit page loads with optional query `?couponId=` for update mode. |
| **Short Description** | Form captures **code**, **title**, **calculation type** (flat amount vs percentage), **amount**, **max usage**, **expiry** (end of local day sent as ISO), **applicable service groups** (multi-select from a fixed list), and **excluded services** (multi-select from subscription catalog by service code). Submits create or update via the **payment** HTTP API with `admin: true`. Session uses `getUser` (verified email gate); service labels for exclusions load from **subscription** `getServices(clientType)` (default `main`). |
| **Variants / Markets** | Production hosts reference **SG** (`payment-api.sleek.sg`, `api.sleek.sg`); admin/cookie flows also surface **HK** domains in shared constants. Per-tenant coupon rules beyond URL env — **Unknown** without payment-service config review. |
| **Dependencies / Related Flows** | **Payment service** (`payment-api.js`): REST `GET/POST/PUT /coupons`, `GET /coupons/:id` — persistence and validation of coupon records (server-side). **Subscription service** (`api.getServices`): catalog for **exclude services** options. **Main API** (`api.getUser`): `GET /admin/users/me` for session; unverified users redirected to `/verify/`. Downstream: customer **checkout / lock coupon** flows use separate endpoints (e.g. `lockCoupon` on main API in `api.js`) — not part of this admin form. |
| **Service / Repository** | **sleek-website** (admin UI, `payment-api.js`, `api.js`, `constants.js`). **Payment API** (coupon CRUD — implementation not in this repo). **Subscription API** (services list). |
| **DB - Collections** | **Unknown** from these view files (coupon storage is in the payment backend). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | On edit load, `getCoupon` maps `excludedServices` using `this.state.serviceItems` from `getServices`; if `getCoupon` resolves before `getServices`, excluded-service labels may not resolve (race). Whether legacy `api.js` `getCoupons` / `createCoupon` / `updateCoupon` against `${getBaseUrl()}/coupons` is still used for other screens vs this **payment-api**-backed flow — **Unknown** without full repo search. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/new-coupons/create-edit.js` (`AdminCouponsCreateEditView`)

- **Bootstrap**: `domready` → `ReactDOM.render` → `AdminLayout` with `hideDrawer={true}`, `sidebarActiveMenuItemKey="new-coupons"`.
- **Session**: `getUser()` → redirect to `/verify/` if `registered_at` is null; else `setState({ user })`.
- **Service catalog**: `getServices(clientType)` with default `clientType` `"main"` for excluded-service picklist (`renderServicesList` maps `code` / `name`).
- **Edit load**: URL `couponId` → `getCouponDetail(couponId)` → hydrates form: `code`, `title`, `calculationType`, `amount`, `maxUsage`, `expiredAt`, `applicableServiceGroups` (string array → react-select options), `excludedServices` (codes matched to `serviceItems`).
- **Calculation types**: `flat` | `percentage` (`renderCalculationTypeOptions`).
- **Applicable groups**: options from `NEW_COUPON_APPLICABLE_SERVICES` (`renderApplicableOptions`).
- **Submit body**: JSON with `calculationType` as enum string, `applicableServiceGroups` and `excludedServices` as string arrays, `expiredAt` as `moment(…).endOf("day").toISOString()`, numeric `maxUsage` and `amount`.
- **Persist**: `couponId` present → `paymentApi.updateCoupon(couponId, { body, admin: true })`; else `paymentApi.createCoupon({ body, admin: true })`. Success → `window.location.href = '/admin/new-coupons'`.
- **Navigation**: Back/cancel → `/admin/new-coupons`.

### `src/utils/payment-api.js`

- **Base URL**: `process.env.PAYMENT_API` or dev `http://localhost:3020`, prod `https://payment-api.sleek.sg`.
- **Coupons**: `getCouponList` → `GET …/coupons`; `getCouponDetail(id)` → `GET …/coupons/${id}`; `createCoupon` → `POST …/coupons`; `updateCoupon(couponId)` → `PUT …/coupons/${couponId}`; `deleteCoupon` → `DELETE …/coupons/${id}`; `getCouponUsages` → `GET …/coupons/${id}/usages`.
- **Transport**: `getDefaultHeaders`, shared `handleResponse` / auth checks with `checkResponseIfAuthorized`.

### `src/utils/api.js` (coupon-adjacent and dependencies)

- **User**: `getUser` → `GET ${getBaseUrl()}/admin/users/me` (via `getResource` — path includes `admin`).
- **Services**: `getServices(clientType)` → `GET ${getBaseSubscriptionServiceUrl()}/services?clientType=…` (subscription service; prod `https://api.sleek.sg` in env `production`).
- **Alternate coupon surface** (not used by this view but same domain): `getCoupons` / `createCoupon` / `updateCoupon` / `deleteCoupon` → `${getBaseUrl()}/coupons` (main API host); `lockCoupon` → `POST …/coupons/lock` for checkout locking.

### `src/utils/constants.js`

- **`NEW_COUPON_APPLICABLE_SERVICES`**: string array — `general`, `accounting`, `accounting-add-on`, `corpsec`, `corpsec-add-on`, `corporate_secretary`, `immigration`, `mailroom`, `business_account`.
- **`ADMIN_RESOURCES`**: includes `{ value: "coupons", label: "Coupons", sidebarMenuItemKeys: ["coupons"], … }` (legacy sidebar key; this screen uses `new-coupons` in the view).
- **`COUPON_APPLICABLE_SERVICES`**: older structured list (`general`, `accountingPlan`, `corpSec`) — not imported by `create-edit.js`.
