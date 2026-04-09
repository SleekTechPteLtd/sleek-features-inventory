# Client Request – Open Bank Account

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Client Request – Open Bank Account |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client / Company Director |
| **Business Outcome** | Connects clients with Singapore local and online banks to open a corporate bank account, reducing friction in the post-incorporation journey. |
| **Entry Point / Surface** | Client App > Requests > Request > Open Bank Account > Create a New Request |
| **Short Description** | Client selects preferred Singapore local or online banks, acknowledges requirements, and gets connected with bankers. Form fill < 5 mins; processing instant (Sleek) / up to 2 weeks (banks). Free. Steps: Select Banks > Acknowledge requirements > Get connected with Bankers. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | Third-party bank referral integrations |
| **Service / Repository** | customer-main, customer-common, customer-root (client shell and shared UI) |
| **DB - Collections** | — |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which banks are supported? Is this a referral or a managed process? |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### customer-main

- **Requests hub:** `src/modules/customer-requests/components/CustomerRequestContent.vue` — catalogue item `type == 'bank-account-opening'` (`BankWidgetIcon`), gated by `open_bank_account` app feature; uses `GetCompanyOpenBankAccountProxy` / `upsert` APIs.
- **Dashboard widget:** `src/modules/dashboard/components/DashboardBankAccountWidget.vue` with `proxies/back-end/company/get-open-bank-account.js` and `update-open-bank-account.js` (`/v2/company/:id/open-bank-account`, bank-account widget flags).

### customer-common

- Shared dashboard / layout where the widget may surface.

### customer-root

- `src/root-config.js`.

### Live app walkthrough

- Confirms bank picker, acknowledgements, and referral-style completion.
