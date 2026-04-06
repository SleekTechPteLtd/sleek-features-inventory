# CorpSec domain inventory

This folder holds draft **Corpsec** rows from the shared master sheet, grouped by **entry-point surface** (`Admin App` vs `Client App`).

## Layout

| Folder | Use |
|--------|-----|
| **`admin-app/`** | One markdown file per master-sheet row whose *Entry Point / Surface* is the **Admin App** (72 files). |
| **`client-app/`** | One markdown file per master-sheet row whose *Entry Point / Surface* is the **Client App** (13 files). Evidence: **customer-main**, **customer-common**, **customer-root**. |
| **`company-register-management.md`** | Legacy sample capability doc (kept for reference). |

Regenerate from CSV:

```bash
python3 scripts/generate-corpsec-admin-app-md.py   # skips view-and-search-company-list.md
python3 scripts/generate-corpsec-client-app-md.py
```

## Client App — feature index

Sorted by slug (same as `domain-corpsec.html`). Sheet **Disposition** for these rows is *Unknown* (no `[Must-have]` tag).

- [Client Portal – Company Secretary File Browser](./client-app/client-portal-company-secretary-file-browser.md)
- [Client Portal – History of Requests View](./client-app/client-portal-history-of-requests-view.md)
- [Client Portal – On-going Requests View](./client-app/client-portal-on-going-requests-view.md)
- [Client Request – Appointment of New Director](./client-app/client-request-appointment-of-new-director.md)
- [Client Request – Change Company Address](./client-app/client-request-change-company-address.md)
- [Client Request – Change Company Name](./client-app/client-request-change-company-name.md)
- [Client Request – Change of Business Activity](./client-app/client-request-change-of-business-activity.md)
- [Client Request – Change of Director](./client-app/client-request-change-of-director.md)
- [Client Request – Change of Officer's Particulars](./client-app/client-request-change-of-officer-s-particulars.md)
- [Client Request – Change of Shareholder's Particulars](./client-app/client-request-change-of-shareholder-s-particulars.md)
- [Client Request – Open Bank Account](./client-app/client-request-open-bank-account.md)
- [Client Request – Resignation of Director](./client-app/client-request-resignation-of-director.md)
- [Client Request – Update My Details](./client-app/client-request-update-my-details.md)

More detail: [client-app/README.md](./client-app/README.md).

## Admin App — feature index

Sorted by filename. `[Must-have]` matches **Disposition** = *Must Keep* on the sheet.

- [Must-have] [Add Employees to Auto-sign Configuration](./admin-app/add-employees-to-auto-sign-configuration.md)
- [Must-have] [Add Internal Comment to Company](./admin-app/add-internal-comment-to-company.md)
- [AGM & Annual Return Workflow](./admin-app/agm-and-annual-return-workflow.md)
- [Amend Company Share Structure Workflow](./admin-app/amend-company-share-structure-workflow.md)
- [Appointment of Director Workflow](./admin-app/appointment-of-director-workflow.md)
- [Must-have] [Browse & Manage Company Mailroom](./admin-app/browse-and-manage-company-mailroom.md)
- [Must-have] [Browse Company File Store](./admin-app/browse-company-file-store.md)
- [Change of Director Workflow](./admin-app/change-of-director-workflow.md)
- [Company Deadlines Workflow](./admin-app/company-deadlines-workflow.md)
- [Company Incorporation Workflow (HK)](./admin-app/company-incorporation-workflow-hk.md)
- [Company Incorporation Workflow (SG)](./admin-app/company-incorporation-workflow-sg.md)
- [Company Incorporation Workflow (UK)](./admin-app/company-incorporation-workflow-uk.md)
- [Must-have] [Create Company – Incorporation](./admin-app/create-company-incorporation.md)
- [Must-have] [Create Company – Transfer](./admin-app/create-company-transfer.md)
- [Must-have] [Create Document Template](./admin-app/create-document-template.md)
- [Must-have] [Create Folder in Company File Store](./admin-app/create-folder-in-company-file-store.md)
- [Must-have] [Create New Request](./admin-app/create-new-request.md)
- [Must-have] [Create Request Template](./admin-app/create-request-template.md)
- [Must-have] [Delete Document Template](./admin-app/delete-document-template.md)
- [Must-have] [Download & Delete Company Files](./admin-app/download-and-delete-company-files.md)
- [Must-have] [Edit Company Business Profile](./admin-app/edit-company-business-profile.md)
- [Must-have] [Edit Company Information & Business Activity Codes](./admin-app/edit-company-information-and-business-activity-codes.md)
- [Must-have] [Edit Document Template](./admin-app/edit-document-template.md)
- [Must-have] [Edit Request Document Content](./admin-app/edit-request-document-content.md)
- [Must-have] [Edit Request Template](./admin-app/edit-request-template.md)
- [Must-have] [Filter & Sort Company List](./admin-app/filter-and-sort-company-list.md)
- [Must-have] [Filter Auto-sign Employee List](./admin-app/filter-auto-sign-employee-list.md)
- [Must-have] [Generate Document from Template](./admin-app/generate-document-from-template.md)
- [Must-have] [Generate Standard Folder Structure](./admin-app/generate-standard-folder-structure.md)
- [Must-have] [Manage AU Tax Registrations](./admin-app/manage-au-tax-registrations.md)
- [Must-have] [Manage Company Admins & Transfer Ownership](./admin-app/manage-company-admins-and-transfer-ownership.md)
- [Must-have] [Manage Company Secretaries](./admin-app/manage-company-secretaries.md)
- [Must-have] [Manage Corporate Shareholders](./admin-app/manage-corporate-shareholders.md)
- [Must-have] [Manage Corporate Trust Shareholders](./admin-app/manage-corporate-trust-shareholders.md)
- [Must-have] [Manage Designated Representatives](./admin-app/manage-designated-representatives.md)
- [Must-have] [Manage Directors](./admin-app/manage-directors.md)
- [Must-have] [Manage Individual Shareholders](./admin-app/manage-individual-shareholders.md)
- [Must-have] [Manage Individual Trust Shareholders](./admin-app/manage-individual-trust-shareholders.md)
- [Must-have] [Manage Nominee Directors](./admin-app/manage-nominee-directors.md)
- [Must-have] [Manage Public Officers](./admin-app/manage-public-officers.md)
- [Must-have] [Manage Registrable Controllers](./admin-app/manage-registrable-controllers.md)
- [Must-have] [Manage Sales Point of Contact](./admin-app/manage-sales-point-of-contact.md)
- [Must-have] [Manage Share Classes](./admin-app/manage-share-classes.md)
- [Must-have] [Manage Significant Controllers Register](./admin-app/manage-significant-controllers-register.md)
- [Must-have] [Manage Standard Users](./admin-app/manage-standard-users.md)
- [Must-have] [Manage Ultimate Beneficial Owners (UBOs)](./admin-app/manage-ultimate-beneficial-owners-ubos.md)
- [Must-have] [Manually Upload AR Filing Documents](./admin-app/manually-upload-ar-filing-documents.md)
- [Must-have] [Notify Company Owner (Mailroom)](./admin-app/notify-company-owner-mailroom.md)
- [Must-have] [Remove Request Template](./admin-app/remove-request-template.md)
- [Resignation of Director Workflow](./admin-app/resignation-of-director-workflow.md)
- [Must-have] [Save Request as PDF](./admin-app/save-request-as-pdf.md)
- [Must-have] [Search Files in Company File Store](./admin-app/search-files-in-company-file-store.md)
- [Must-have] [Select Company & Workflow for AR Filing](./admin-app/select-company-and-workflow-for-ar-filing.md)
- [Must-have] [Send Request to SleekSign](./admin-app/send-request-to-sleeksign.md)
- [Share Transfer Workflow (SG)](./admin-app/share-transfer-workflow-sg.md)
- [Must-have] [Start Deadlines Workflow](./admin-app/start-deadlines-workflow.md)
- [Must-have] [Toggle Automated Signature per Employee](./admin-app/toggle-automated-signature-per-employee.md)
- [Must-have] [Update Request Document Data](./admin-app/update-request-document-data.md)
- [Must-have] [Update Request Status](./admin-app/update-request-status.md)
- [Must-have] [Upload Files to Company File Store](./admin-app/upload-files-to-company-file-store.md)
- [Must-have] [View & Edit Company Core Details](./admin-app/view-and-edit-company-core-details.md)
- [Must-have] [View & Edit Staff Assigned to Company](./admin-app/view-and-edit-staff-assigned-to-company.md)
- [Must-have] [View & Manage Company Deadlines](./admin-app/view-and-manage-company-deadlines.md)
- [Must-have] [View & Search Company List](./admin-app/view-and-search-company-list.md)
- [Must-have] [View & Search Requests List](./admin-app/view-and-search-requests-list.md)
- [Must-have] [View AR Filing Source Documents](./admin-app/view-ar-filing-source-documents.md)
- [Must-have] [View Auto-sign Employee List](./admin-app/view-auto-sign-employee-list.md)
- [Must-have] [View CDD Questionnaire History](./admin-app/view-cdd-questionnaire-history.md)
- [Must-have] [View Company as Client](./admin-app/view-company-as-client.md)
- [Must-have] [View Document Templates List](./admin-app/view-document-templates-list.md)
- [Must-have] [View Request Templates List](./admin-app/view-request-templates-list.md)
- [Must-have] [View Workflows Related to Company](./admin-app/view-workflows-related-to-company.md)

## Sample capability doc (legacy)

- [company-register-management.md](./company-register-management.md)
