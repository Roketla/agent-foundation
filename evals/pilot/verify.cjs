// Manual pilot only. Uses an existing Playwright installation; CI stays offline.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { createHash } = require('node:crypto');

async function main() {
  const [site, destination] = process.argv.slice(2);
  if (!site || !destination) throw new Error('Usage: node verify.cjs SITE_HTML OUTPUT_DIR');
  const output = path.resolve(destination);
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, reducedMotion: 'reduce' });
  const errors = [], external = [], checks = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => { if (/^https?:/.test(request.url())) external.push(request.url()); });
  const check = async (name, action) => {
    try { await action(); checks.push({ name, passed: true }); }
    catch (error) { checks.push({ name, passed: false, detail: error.message }); }
  };
  try {
    await page.goto(pathToFileURL(path.resolve(site)).href);
    const button = page.getByRole('button', { name: 'Mostrar el resum local' });
    const name = page.getByLabel('Nom', { exact: true });
    const email = page.getByLabel('Correu electrònic');
    const service = page.getByLabel("Servei d'interès");
    const result = page.getByRole('status');
    await check('Keyboard skip link has visible focus', async () => {
      await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(() => document.activeElement.textContent), 'Vés al contingut');
      assert.ok(await page.evaluate(() => parseFloat(getComputedStyle(document.activeElement).outlineWidth) >= 2));
      await page.keyboard.press('Enter');
      assert.ok(page.url().endsWith('#contingut'));
    });
    await check('Services and contact navigation work', async () => {
      await page.getByRole('link', { name: 'Serveis', exact: true }).click();
      assert.ok(page.url().endsWith('#serveis'));
      await page.getByRole('link', { name: 'Contacte', exact: true }).click();
      assert.ok(page.url().endsWith('#contacte'));
    });
    await check('Empty form rejects submission and focuses the first error', async () => {
      await button.click();
      assert.ok(await result.isHidden());
      assert.equal(await name.getAttribute('aria-invalid'), 'true');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'name');
    });
    await check('Invalid email rejects submission', async () => {
      await name.fill('Laia Prova');
      await email.fill('incorrecte');
      await service.selectOption({ label: 'Web corporatiu' });
      await button.click();
      assert.ok(await result.isHidden());
      assert.equal(await email.getAttribute('aria-invalid'), 'true');
    });
    await check('Whitespace-only name is rejected', async () => {
      await name.fill('   ');
      await email.fill('laia@example.test');
      await button.click();
      assert.ok(await result.isHidden());
    });
    await check('Valid request renders selected service as local summary', async () => {
      await name.fill('Laia Prova');
      await button.click();
      await result.waitFor({ state: 'visible' });
      const summary = await result.textContent();
      assert.match(summary, /Laia Prova/);
      assert.match(summary, /Web corporatiu/);
      assert.match(summary, /no s'ha enviat cap missatge/);
      assert.equal(await result.getAttribute('aria-live'), 'polite');
    });
    await check('Repeated submission does not duplicate the summary', async () => {
      await button.click();
      assert.equal(await result.getByRole('heading').count(), 1);
    });
    await page.screenshot({ path: path.join(output, 'desktop.png'), fullPage: true });
    await check('390px viewport has no horizontal overflow', async () => {
      await page.setViewportSize({ width: 390, height: 844 });
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      await page.screenshot({ path: path.join(output, 'mobile.png'), fullPage: true });
    });
    await check('No external requests or JavaScript errors', async () => {
      assert.deepEqual(external, []);
      assert.deepEqual(errors, []);
    });
  } finally {
    const report = { browser: browser.version(), site_sha256: createHash('sha256').update(fs.readFileSync(site)).digest('hex'), checks };
    fs.writeFileSync(path.join(output, 'verification.json'), JSON.stringify(report, null, 2) + '\n');
    await browser.close();
  }
  console.log(JSON.stringify({ passed: checks.filter(c => c.passed).length, failed: checks.filter(c => !c.passed).length, output }));
  if (checks.some(c => !c.passed)) process.exitCode = 1;
}
main().catch(error => { console.error(error.message); process.exitCode = 1; });
