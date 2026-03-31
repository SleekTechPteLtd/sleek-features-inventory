# Sleek Feature Scope Audit

Rapid first-pass project to inventory the business capabilities currently present across Sleek domains, so the principals can estimate functional scope before discussing architecture or solution design.

## Feature Master Sheet

[Sleek Feature Scope Audit Master Sheet](https://docs.google.com/spreadsheets/d/1-8-fY-WRoXcbBYsz5XQgLYVhuUKN2Q6GQmXitJNRvGs/edit?usp=sharing)

Add a new row using the hover button shown here:



## Goal

Produce a shared, stakeholder-reviewable first-pass feature inventory across domains within 1-2 weeks.

## Outcome We Want

- A single master spreadsheet covering features across domains  
- A first-pass estimate of how much functional scope exists  
- Visibility into obvious overlap, simplification opportunities, and gaps  
- Enough shared understanding to support later planning work

## Working Principles

- Audit at the level of **user capability / business feature**  
- Focus on **UI, workflows, and business outcomes**, not code structure  
- Each principal owns the **first pass** for their domain  
- Use **one shared master sheet** and include a Domain field so we can re-order  
- Review **daily** to align, de-duplicate, and unblock  
- Do not try to centrally validate every feature row  
- Treat the output as a **living first pass**, not final truth

## What Counts as a Feature

A feature is a **user-meaningful capability with a business outcome**.

Good examples:

- Customer completes an accounting onboarding questionnaire  
- User uploads receipts for bookkeeping processing  
- Receipt is processed and added as an expense  
- Finance user reviews and approves categorisation results

Not features:

- A single screen or component  
- An API endpoint  
- A workflow engine step  
- A repo, service, or database table

These can be used as evidence, but they are not the inventory unit.

## Audit Process

1. Agree the shared spreadsheet columns and lightweight feature definition.
2. Each principal captures a first pass for their domain.
3. Use short daily reviews to resolve overlaps, shared ownership, and obvious inconsistencies.
4. Schedule validation with **product owners** so they can confirm, correct, and fill gaps (after the first pass from discovery sources).
5. End with a first estimate of scope plus explicit open question

## Spreadsheet Columns

Each column has a **type**. Use **enums** (fixed pick-lists) where listed. Everywhere else use free text. In Google Sheets you can enforce enums with **Data validation** on the column.


| Column                       | Type | Allowed values / notes                                                                                                                                                                                                                         |
| ---------------------------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Domain                       | Enum | `Corpsec, Compliance, SBC, Bookkeeping & Accounting, Sleeksign, CLM, Platform, SDET, RPA, AI/ML, Marketing`                                                                                                                                    |
| Feature Name                 | Text | Short name of the capability                                                                                                                                                                                                                   |
| Canonical Owner              | Text | Person name (principal accountable for the row)                                                                                                                                                                                                |
| Primary User / Actor         | Text | Who triggers or uses the feature                                                                                                                                                                                                               |
| Business Outcome             | Text | Why the feature exists from a business perspective                                                                                                                                                                                             |
| Entry Point / Surface        | Text | Where it shows up (UI area, app, workflow entry)                                                                                                                                                                                               |
| Short Description            | Text | What the feature does                                                                                                                                                                                                                          |
| Variants / Markets           | Text | Country, market, or product differences                                                                                                                                                                                                        |
| Dependencies / Related Flows | Text | Upstream, downstream, cross-domain links                                                                                                                                                                                                       |
| Service / Repository         | Text | Any / all services used for feature                                                                                                                                                                                                            |
| DB Collections               | Text | DB and collection used for feature                                                                                                                                                                                                             |
| Evidence Source              | Text | Free text. Describe where this row came from (for example QA screenshots, live app walkthrough, tests, codebase, stakeholder, Admin 2.0 docs). You can use short labels or full sentences. Separate multiple sources with a comma if you like. |
| Criticality                  | Enum | `High`, `Medium`, `Low`, `Unknown`                                                                                                                                                                                                             |
| Usage Confidence             | Enum | `High`, `Medium`, `Low`, `Unknown`                                                                                                                                                                                                             |
| Disposition                  | Enum | `Must Keep`, `Keep but Simplify`, `Merge`, `Defer`, `Retire`, `Unknown`                                                                                                                                                                        |
| Open Questions               | Text | Follow-ups, or leave blank if none                                                                                                                                                                                                             |
| Reviewer                     | Text | Who last reviewed the row (empty if not yet reviewed)                                                                                                                                                                                          |
| Review Status                | Enum | `Draft`, `Reviewed`, `Challenged`, `Confirmed`                                                                                                                                                                                                 |


## Potential sources of truth (where to look first)

These three are the main places to build a **first pass** before you schedule validation with **product owners** (see below). They are discovery channels, not the final word on scope.

1. **QA Tech (Slack channel).** Use it to talk to QAs, ask questions, and get access to what they already have (screenshots, coverage knowledge, how they group work by domain). This is the human route into QA artefacts, not only a static folder.
2. **Sleek Admin 2.0 (unfinished).** There was an attempt to build a new admin experience. It was never finished, but there was a **plan** and **design**. We need to **locate** those materials (wiki, Figma, drive, tickets, repo docs). Whatever exists may still reflect intended scope or IA even if the build stopped.
3. **Your own apps in the domain.** Spin up the apps that matter for your domain, click through flows, and **take your own screenshots** where helpful. Bookkeeping and similar areas may sit under **multiple apps**, but the footprint is still small enough to walk through without treating the codebase as the inventory source.

Together these give enough material for a first-pass spreadsheet. Gaps are expected.

## Supporting sources (optional, per row)

Use whatever order fits each row. Combine with the three channels above where useful.

- **QA screenshot library** (when you have access). Roughly **60% coverage** of features by domain. Strong when you need “what exists in the UI” without starting from code.  
- **Automated tests.** Front-end and **E2E / feature tests** where they exist. Good for paths that are supposed to work. Missing tests do not mean a feature is unimportant.  
- **Codebase.** Supporting evidence for wiring and edge cases. **Not** the primary shape of the inventory (see Working Principles).

## Validation (after the first pass)

Schedule **meetings with product owners** to validate the inventory. That step is **business-led**, not a tech-only review. Use it to confirm criticality, correct mistakes, and catch missing capabilities. Tech can help answer “how does this work today?” but product owners own “what must the product do?”

## Notes on Evidence

- Prefer **UI, workflows, stakeholder knowledge, QA artefacts, and business outcomes** over repo archaeology.  
- Code supports discovery but should not define what counts as a feature.

## Review Cadence

- Principal DSM sync for alignment and de-duplication  
- **Product owner** sessions for validation after the first pass (scheduled meetings, business-led)  
- The aim is not to review every row in depth, but to improve the first pass quickly

## Non-Goals

- No target architecture decisions yet  
- No solution design yet  
- No implementation planning yet  
- No attempt to prove complete feature parity at this stage

## Definition of Done for This Audit

- Each domain has a populated first pass  
- All rows live in one master sheet  
- Shared features have a canonical owner  
- Product owners have started correcting and filling gaps (validation meetings)  
- We have a clearer view of the size and shape of the functional estate

## Open Questions

- Where are the **Sleek Admin 2.0** plan and design artefacts stored?  
- Are we missing any product domains?

