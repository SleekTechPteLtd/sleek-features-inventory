# Mark RCD review as complete

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Mark RCD review as complete |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Director or main signee (user who passes `canManageCompanyMiddleware("directorMainSignee")` after authentication) |
| **Business Outcome** | Registrable controller declaration (RCD) data is formally marked as reviewed and completed so the incorporation or registration workflow can advance past the RCD review gate. |
| **Entry Point / Surface** | Sleek Back HTTP API: `PUT /companies/:companyId/registrable-controller-declaration/review-and-complete`. Requires `userService.authMiddleware` and `companyService.canManageCompanyMiddleware("directorMainSignee")`. Typical caller is the Sleek incorporation / company setup flow where directors or signees confirm the RCD step. |
| **Short Description** | Sets `is_review_and_completed` to `true` on all `RegistrableControllerDeclaration` documents for the given company via `updateMany`. No request body beyond implicit `companyId` from the route. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream** — RCD rows created or updated via `POST /companies/:companyId/registrable-controller-declaration` and related delete flows. **Related** — `GET /companies/:companyId/registrable-controller-declaration` returns data (broader `companyUser` guard); `GET .../generate-document` builds PDF after review. **Downstream** — Any client or workflow that keys off `is_review_and_completed` on RCD records or company registration state. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `registrablecontrollerdeclarations` (Mongoose model `RegistrableControllerDeclaration` in `schemas/registrable-controller-declaration.js`; default pluralized collection name — not overridden in schema). Updates by `company` ObjectId. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Is `is_review_and_completed` consumed only in the incorporation app or also in other services (event/webhook)? `updateRegistrableControllerDeclarationToReviewAndComplate` uses `find` then checks `if (!company)` on an array (always truthy when empty array); confirm intended guard vs bug. Typo in exported name `Complate` vs `Complete` — any external callers depending on the string? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/registrable-controller-declaration-controller.js`

- **`PUT`** `/companies/:companyId/registrable-controller-declaration/review-and-complete` — **`userService.authMiddleware`**, **`companyService.canManageCompanyMiddleware("directorMainSignee")`**
- Payload: **`{ companyId: req.params.companyId }`** only
- Delegates to **`updateRegistrableControllerDeclarationToReviewAndComplate(payload)`** — response **`{ message: "Successfully Review and completed!" }`**

### `services/registrable-controller-declaration/registrable-controller-declaration-service.js`

- **`updateRegistrableControllerDeclarationToReviewAndComplate(payload, res)`** — sanitizes payload
- **`RegistrableControllerDeclaration.find({ company: sanitizePayload.companyId })`** — existence check (see open questions)
- **`RegistrableControllerDeclaration.updateMany({ "company": sanitizePayload.companyId }, { "$set": { "is_review_and_completed": true } })`**

### `schemas/registrable-controller-declaration.js`

- **`RegistrableControllerDeclaration`** schema includes **`is_review_and_completed: { type: Boolean, defaultValue: false }`**, plus **`company`**, **`author`**, **`user`**, **`company_user`**, **`is_completed`**, **`data`**, timestamps
