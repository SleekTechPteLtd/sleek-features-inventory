#!/usr/bin/env node
/**
 * Captures screenshots of admin app accounting + corpsec features from admin-sit.sleek.sg
 * Auth is injected from ~/Downloads/admin-app-localstorage.json (exported from live session)
 *
 * Usage: node scripts/capture-admin-app-screenshots.mjs
 */

import { chromium } from 'playwright';
import { readFileSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUTPUT_BASE = join(__dirname, '..', 'by-surface', 'admin-app', 'screenshots');
const AUTH_FILE = join(process.env.HOME, 'Downloads', 'admin-app-localstorage.json');
const BASE_URL = 'https://admin-sit.sleek.sg';
const CID = '6768ce4b939e53003e993169';
const VIEWPORT = { width: 1400, height: 900 };

// Load session auth from downloaded localStorage export
const authData = JSON.parse(readFileSync(AUTH_FILE, 'utf8'));

// Ensure output directories exist
for (const section of [
  'company', 'workflows', 'users', 'tools',
  'corpsec-company', 'corpsec-people', 'corpsec-requests', 'corpsec-filestore',
]) {
  mkdirSync(join(OUTPUT_BASE, section), { recursive: true });
}

/** `/admin/files/` — open company picker (label "Select Company"), search "Draft", select first result row. */
async function selectFirstCompanyFromAdminFilesPicker(page) {
  const openPicker = async () => {
    const byLabel = page.getByLabel('Select Company', { exact: true });
    if (await byLabel.count()) {
      await byLabel.click();
      return;
    }
    const byRole = page.getByRole('combobox', { name: /select company/i });
    if (await byRole.count()) {
      await byRole.click();
      return;
    }
    const byFilter = page
      .locator('button, [role="combobox"], [class*="select"]')
      .filter({ hasText: 'Select Company' })
      .first();
    if (await byFilter.count()) {
      await byFilter.click();
      return;
    }
    const label = page.getByText('Select Company', { exact: true }).first();
    await label.waitFor({ state: 'visible', timeout: 15000 });
    const fromLabel = label.locator(
      'xpath=ancestor::*[self::button or @role="combobox"][1]',
    );
    if (await fromLabel.count()) {
      await fromLabel.click();
    } else {
      await label.click();
    }
  };

  await openPicker();
  await page.waitForTimeout(600);

  const popoverSelectors = [
    '.bp3-popover-open',
    '.bp4-popover-open',
    '.bp5-popover-open',
  ];
  let popover = page.locator(popoverSelectors.join(', ')).first();
  try {
    await popover.waitFor({ state: 'visible', timeout: 5000 });
  } catch {
    popover = page
      .locator('.bp3-popover .bp3-popover-content, .bp4-popover .bp4-popover-content, .bp5-popover .bp5-popover-content')
      .last();
    await popover.waitFor({ state: 'visible', timeout: 8000 }).catch(() => {});
  }

  let searchInput = popover.getByPlaceholder('Filter...').first();
  if (!(await searchInput.count())) {
    searchInput = popover.locator('input[placeholder*="Filter"]').first();
  }
  if (!(await searchInput.count())) {
    searchInput = popover.locator(
      'input.bp3-input, input.bp4-input, input.bp5-input, input[type="search"], input[type="text"]',
    ).first();
  }
  if (await searchInput.count()) {
    await searchInput.fill('Draft');
    await page.waitForTimeout(1200);
  }

  const item = popover
    .locator('.bp3-menu .bp3-menu-item, .bp4-menu .bp4-menu-item, .bp5-menu .bp5-menu-item')
    .filter({ hasNot: page.locator('input') })
    .first();
  if (await item.count()) {
    await item.click();
    await page.waitForTimeout(2500);
  }
}

const features = [
  // ── Company Management ─────────────────────────────────────────────────────
  {
    slug: 'company/company-list',
    url: '/admin/companies/',
  },
  {
    slug: 'company/company-overview',
    url: `/admin/company-overview/?cid=${CID}`,
  },
  {
    slug: 'company/company-accounting',
    url: `/admin/company-overview/?cid=${CID}&currentPage=Accounting`,
  },
  {
    slug: 'company/company-billing-subscriptions',
    url: `/admin/company-overview/?cid=${CID}&currentPage=Billing+Beta`,
  },
  {
    slug: 'company/company-billing-invoices',
    url: `/admin/company-overview/?cid=${CID}&currentPage=Billing+Beta`,
    interact: async (page) => {
      const tab = page.locator('text=INVOICES & CREDIT NOTE').first();
      if (await tab.count()) {
        await tab.click();
        await page.waitForTimeout(1500);
      }
    },
  },
  {
    slug: 'company/company-billing-payment-request',
    url: `/admin/company-overview/?cid=${CID}&currentPage=Billing+Beta`,
    interact: async (page) => {
      const btn = page.locator('text=PAYMENT REQUEST, button:has-text("Payment Request")').first();
      if (await btn.count()) {
        await btn.click();
        await page.waitForTimeout(1500);
      }
    },
  },
  {
    slug: 'company/company-deadlines',
    url: `/admin/company-overview/?cid=${CID}&currentPage=Deadlines`,
  },

  // ── Workflows & Requests ───────────────────────────────────────────────────
  {
    slug: 'workflows/workflow-list',
    url: '/admin/new-workflow/',
  },
  {
    slug: 'workflows/camunda-workflows',
    url: '/admin/sleek-workflow/',
  },
  {
    slug: 'workflows/requests-list',
    url: '/admin/requests/',
  },
  {
    slug: 'workflows/request-detail',
    url: '/admin/requests/',
    interact: async (page) => {
      // Hover over the first row to highlight it — avoid clicking Edit (may trigger dialog)
      const firstRow = page.locator('table tbody tr, [class*="row"]').first();
      if (await firstRow.count()) await firstRow.hover();
      await page.waitForTimeout(500);
    },
  },

  // ── Users & KYC ───────────────────────────────────────────────────────────
  {
    slug: 'users/user-list',
    url: '/admin/user-management/',
  },
  {
    slug: 'users/user-detail',
    url: '/admin/user-management/',
    interact: async (page) => {
      // Navigate directly via the EDIT link href (avoids dialog risk)
      const editLink = page.locator('a:has-text("EDIT"), a[href*="user"]').first();
      if (await editLink.count()) {
        const href = await editLink.getAttribute('href');
        if (href) {
          await page.goto(`https://admin-sit.sleek.sg${href}`, { waitUntil: 'load', timeout: 30000 });
          await page.waitForTimeout(5000);
        }
      }
    },
  },
  {
    slug: 'users/user-kyc',
    url: '/admin/user-management/',
    interact: async (page) => {
      // Navigate to user detail, then scroll to KYC section
      const editLink = page.locator('a:has-text("EDIT"), a[href*="user"]').first();
      if (await editLink.count()) {
        const href = await editLink.getAttribute('href');
        if (href) {
          await page.goto(`https://admin-sit.sleek.sg${href}`, { waitUntil: 'load', timeout: 30000 });
          await page.waitForTimeout(5000);
          const kycSection = page.locator('text=KYC').first();
          if (await kycSection.count()) await kycSection.scrollIntoViewIfNeeded();
          await page.waitForTimeout(500);
        }
      }
    },
  },

  // ── Admin Tools ────────────────────────────────────────────────────────────
  {
    slug: 'tools/audit-logs',
    url: '/admin/audit-logs/',
  },
  {
    slug: 'tools/document-templates',
    url: '/admin/documents/',
  },
  {
    slug: 'tools/request-templates',
    url: '/admin/request-templates/',
  },

  // ══════════════════════════════════════════════════════════════════════════
  // CorpSec screenshots
  // ══════════════════════════════════════════════════════════════════════════

  // ── Company Management ─────────────────────────────────────────────────────
  {
    slug: 'corpsec-company/company-list',
    url: '/admin/companies/',
  },
  {
    slug: 'corpsec-company/company-overview',
    url: `/admin/company-overview/?cid=${CID}&currentPage=Overview`,
  },
  {
    slug: 'corpsec-company/company-core-details',
    url: `/admin/company-overview/?cid=${CID}`,
    interact: async (page) => {
      // Click the EDIT button on the overview to open the core details edit form
      const editBtn = page.locator('button:has-text("EDIT"), a:has-text("EDIT")').first();
      if (await editBtn.count()) { await editBtn.click(); await page.waitForTimeout(4000); }
    },
  },
  {
    slug: 'corpsec-company/company-business-profile',
    url: `/admin/company-overview/?cid=${CID}&currentPage=Company+Info`,
    interact: async (page) => {
      // Scroll to the "About the company" / business profile section
      const section = page.locator('text=About the company, text=Business Profile, text=Customer Risk Rating').first();
      if (await section.count()) { await section.scrollIntoViewIfNeeded(); await page.waitForTimeout(2000); }
    },
  },
  {
    slug: 'corpsec-company/company-deadlines',
    url: `/admin/company-overview/?cid=${CID}&currentPage=Deadlines`,
  },

  // ── People & Officers ──────────────────────────────────────────────────────
  {
    slug: 'corpsec-people/manage-directors',
    url: `/admin/company-overview/?cid=${CID}&currentPage=People+%26+Entities`,
  },
  {
    slug: 'corpsec-people/manage-shareholders',
    url: `/admin/company-overview/?cid=${CID}&currentPage=Shares`,
  },
  {
    slug: 'corpsec-people/manage-ubos',
    url: `/admin/company-overview/?cid=${CID}&currentPage=People+%26+Entities`,
    interact: async (page) => {
      const section = page.locator('text=Beneficial Owner, text=UBO').first();
      if (await section.count()) await section.scrollIntoViewIfNeeded();
      await page.waitForTimeout(500);
    },
  },
  {
    slug: 'corpsec-people/manage-secretaries',
    url: `/admin/company-overview/?cid=${CID}&currentPage=People+%26+Entities`,
    interact: async (page) => {
      const section = page.locator('text=Secretary, text=Secretar').first();
      if (await section.count()) await section.scrollIntoViewIfNeeded();
      await page.waitForTimeout(500);
    },
  },

  // ── Requests & Documents ───────────────────────────────────────────────────
  {
    slug: 'corpsec-requests/requests-list',
    url: '/admin/requests/',
  },
  {
    slug: 'corpsec-requests/request-detail',
    url: '/admin/requests/',
    interact: async (page) => {
      const firstRow = page.locator('table tbody tr, [class*="row"]').first();
      if (await firstRow.count()) await firstRow.hover();
      await page.waitForTimeout(500);
    },
  },
  {
    slug: 'corpsec-requests/document-templates',
    url: '/admin/documents/',
  },
  {
    slug: 'corpsec-requests/request-templates',
    url: '/admin/request-templates/',
  },

  // ── File Store & Mailroom ──────────────────────────────────────────────────
  {
    slug: 'corpsec-filestore/file-store-browser',
    url: '/admin/files/',
    interact: async (page) => {
      await selectFirstCompanyFromAdminFilesPicker(page);
    },
  },
  {
    slug: 'corpsec-filestore/mailroom',
    url: '/admin/mailroom/',
    interact: async (page) => {
      await selectFirstCompanyFromAdminFilesPicker(page);
    },
  },
  {
    slug: 'corpsec-filestore/file-upload',
    url: '/admin/files/',
    interact: async (page) => {
      await selectFirstCompanyFromAdminFilesPicker(page);
      const uploadBtn = page.locator('button:has-text("Upload")').first();
      if (await uploadBtn.count()) { await uploadBtn.click(); await page.waitForTimeout(1500); }
    },
  },
];

async function main() {
  console.log(`Launching browser...`);
  const browser = await chromium.launch({ headless: false, slowMo: 50 });

  const context = await browser.newContext({ viewport: VIEWPORT });

  // Inject all localStorage values before any page loads
  await context.addInitScript((data) => {
    for (const [key, value] of Object.entries(data)) {
      if (value !== null && value !== undefined) {
        localStorage.setItem(key, value);
      }
    }
  }, authData);

  const page = await context.newPage();
  let failed = 0;

  for (const feature of features) {
    const outputPath = join(OUTPUT_BASE, `${feature.slug}.png`);
    console.log(`\n→ ${feature.slug}`);

    try {
      await page.goto(`${BASE_URL}${feature.url}`, { waitUntil: 'load', timeout: 30000 });

      // Check for redirect to login
      const currentUrl = page.url();
      if (currentUrl.includes('/login') || currentUrl.includes('/auth') || currentUrl.includes('auth0')) {
        console.error('  ✗ Redirected to login — token may be expired');
        failed++;
        continue;
      }

      // Wait for data to fully load
      await page.waitForTimeout(5000);

      if (feature.interact) {
        try {
          await feature.interact(page);
        } catch (err) {
          console.warn(`  ⚠ Interaction skipped: ${err.message}`);
        }
      }

      // Wait for the page to fully load
      await page.waitForTimeout(5000);

      await page.screenshot({ path: outputPath, fullPage: false });
      console.log(`  ✓ ${outputPath}`);
    } catch (err) {
      console.error(`  ✗ Failed: ${err.message}`);
      failed++;
    }
  }

  await browser.close();
  console.log(`\n${'─'.repeat(60)}`);
  console.log(`Done. ${features.length - failed}/${features.length} screenshots captured.`);
  if (failed > 0) console.log(`${failed} failed — check output above.`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
