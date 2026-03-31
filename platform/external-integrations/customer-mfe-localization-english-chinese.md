# Customer MFE localization (English/Chinese)

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Customer portal English/Chinese localization switch |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | End users in customer portal (`customer-mfe`) |
| **Business Outcome** | Users can use core customer flows in English or Chinese UI without separate deployments |
| **Entry Point / Surface** | Login page language switch; route query `?lang=HK`; locale cookie `_locale` |
| **Short Description** | `customer-mfe` exposes a localization toggle with `en` and `zh` options. The capability is controlled by CMS app feature `localization` in platform config. On change, app updates URL query (`EN`/`HK`), persists `_locale`, loads locale bundle dynamically (`/src/lang/zh`), maps Vuetify locale to `zhHant`, and broadcasts locale-change topic. |
| **Variants / Markets** | Current language map is `en` (English) and `zh` (Chinese, Traditional/HK UI strings in many places) |
| **Dependencies / Related Flows** | CMS platform config and app features (`cmsAppFeatures.localization`) from `GET /v2/config/platform/customer`; customer routing/query params |
| **Service / Repository** | `customer-mfe` (`customer-main`, `customer-common`); upstream config served by `sleek-back` config endpoints |
| **DB - Collections** | N/A (client-side cookie + config payload driven) |
| **Evidence Source** | Codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | Whether additional locales are planned; translation quality/completeness governance; ownership of copy updates between product and CMS |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### customer-mfe

- `customer-common/src/maps/i18n.js` - available languages include `{ language: "en" }` and `{ language: "zh" }`.
- `customer-common/src/modules/shared/components/localization/LocalizationSwitch.vue` - UI switch component shown when localization is enabled.
- `customer-common/src/mixins/locale-mixin.js` - localization feature flag from `platformConfig.cmsAppFeatures.localization`, locale cookie `_locale`, route query update (`EN`/`HK`), locale loading, locale change event.
- `customer-common/src/utilities/locale-util.js` - dynamic locale import and Vuetify locale mapping (`zh` -> `zhHant`).
- `customer-main/src/App.vue` - initializes locale from `_locale`, supports URL language override (`?lang=HK` -> `zh`), and loads platform config before app initialization.
- `customer-main/src/plugins/vuetify.js` - registers Vuetify `zh-Hant` locale.
- `customer-main/src/modules/login/components/LoginCard.vue` - renders `<LocalizationSwitch />` on login.
- `customer-main/src/lang/en.js`, `customer-main/src/lang/zh.js` - locale message catalogs.

### sleek-back

- Supplies customer platform config used by the feature (`/v2/config/platform/customer`) and CMS-driven app feature flags (see [sleek-cms-sdk-and-platform-config.md](./sleek-cms-sdk-and-platform-config.md)).

## Related

- [sleek-cms-sdk-and-platform-config.md](./sleek-cms-sdk-and-platform-config.md)
- [../scans-pending/customer-mfe/README.md](../scans-pending/customer-mfe/README.md)
