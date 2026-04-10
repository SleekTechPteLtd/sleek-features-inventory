# Manage Discount Coupons (Legacy Admin)

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Discount Coupons (Legacy Admin) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal Admin with `permissions.coupons === "full"` |
| **Business Outcome** | Enables privileged admins to create and maintain promotional discount coupons that reduce client invoice amounts, with controls over discount code, title, amount, usage cap, expiry date, and applicable service scope. |
| **Entry Point / Surface** | Sleek Admin (sleek-website legacy UI) > Coupons (sidebar) |
| **Short Description** | Admins list, create, edit, and remove discount coupons via the legacy sleek-website admin panel. Coupons are configurable with code, title, discount amount (negative value), maximum redemptions, expiry date, and applicable service (General, Accounting, Corpsec). Edit and remove actions are restricted to coupons still in "new" status (i.e. not yet redeemed). Referral-program coupons are hidden from this view. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Invoice generation (coupons applied at billing time); Referral Program (referral_program type excluded from this view); sleek-billings-backend `/coupons` REST API (shared backend); Billing Admin coupon management in sleek-billings-frontend (newer, richer UI) |
| **Service / Repository** | sleek-website (frontend); sleek-billings-backend (API) |
| **DB - Collections** | `coupons` (inferred; same backend as sleek-billings-backend which writes `coupons` and `couponusages`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Is this legacy admin view still actively used, or has it been superseded by the sleek-billings-frontend coupon UI? The `NEW_COUPON_APPLICABLE_SERVICES` constant lists a much broader set of service scopes — is the legacy form intentionally limited to three or is it outdated? Which backend service handles `POST /coupons/lock` and when is it invoked? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Frontend — `src/views/admin/coupons.js` (sleek-website)
- `AdminCouponsView` React component mounted at `#root`; rendered inside `AdminLayout` with `sidebarActiveMenuItemKey="coupons"`
- **Access guard**: create/edit/remove buttons are disabled unless `user.permissions.coupons === "full"` (line 64, 117, 122)
- **List view**: paginated table (50/page) showing code, title, amount, usage (`current_usage_nb / max_usage_nb`), createdAt, expired_at; sortable and filterable columns; referral-program coupons filtered out at render time (`coupon.type !== "referral_program"`)
- **Status guard**: edit and remove disabled when `coupon.status !== "new"` (lines 117–122); once a coupon is redeemed it becomes read-only in this UI
- **Form fields**: coupon_code, coupon_title, coupon_amount (numeric, expected negative — e.g. `-300`), coupon_max_usage_nb, coupon_expired_at (date picker), applicable_service (Select driven by `COUPON_APPLICABLE_SERVICES`)
- **Submit**: creates via `api.createCoupon({ body, admin: true })` or updates via `api.updateCoupon(id, { body, admin: true })`
- **Remove**: confirmation dialog → `api.deleteCoupon(couponId, { admin: true })`

### API layer — `src/utils/api.js` (sleek-website)
| Function | Method | Endpoint | Notes |
|---|---|---|---|
| `getCoupons` | GET | `/coupons` | Query: sortBy, sortOrder, code, title, amount, skip, limit; `admin: true` flag |
| `createCoupon` | POST | `/coupons` | Body: amount, code, title, expired_at, applicable_service, max_usage_nb; `admin: true` |
| `updateCoupon` | PUT | `/coupons/:id` | Same body shape; `admin: true` |
| `deleteCoupon` | DELETE | `/coupons/:id` | `admin: true` |
| `lockCoupon` | POST | `/coupons/lock` | Used elsewhere (not in this admin view) |

### Constants — `src/utils/constants.js` (sleek-website)
- `COUPON_APPLICABLE_SERVICES` (used in legacy form): `general`, `accountingPlan` (Accounting), `corpSec` (Corpsec)
- `NEW_COUPON_APPLICABLE_SERVICES` (broader, used elsewhere): general, accounting, accounting-add-on, corpsec, corpsec-add-on, corporate_secretary, immigration, mailroom, business_account
- Sidebar nav entry: `{value: "coupons", label: "Coupons", sidebarMenuItemKeys: ["coupons"]}` (line 1369)
