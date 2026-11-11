/* Usage: NODE_PATH=<playwright packages> node this-file.cjs <site URL or local folder> <report folder> */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

(async () => {
  const input = process.argv[2];
  const output = path.resolve(process.argv[3]);
  assert(input, 'Pass the website URL or local review-package folder');
  const base = /^https?:/.test(input) ? input.replace(/\/$/, '') + '/' : pathToFileURL(path.resolve(input) + path.sep).href;
  await fs.mkdir(output, {recursive: true});
  const browser = await chromium.launch({headless: true});
  const checks = [];
  const errors = [];
  try {
    for (const size of [{name: 'desktop', width: 1440, height: 1050}, {name: 'mobile', width: 390, height: 844}]) {
      const context = await browser.newContext({viewport: {width: size.width, height: size.height}, deviceScaleFactor: 1});
      const page = await context.newPage();
      page.on('pageerror', error => errors.push(error.message));
      for (const [route, count] of [['manuscript/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.html', 16], ['figures/index.html', 16], ['index.html', 1]]) {
        await page.goto(base + route, {waitUntil: 'networkidle'});
        assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), 'Page must not stretch wider than its viewport');
        const figures = page.locator('.paper-figure');
        assert.equal(await figures.count(), count);
        // Inspect each saved vector at its rendered size, including lazy-loaded images.
        for (let i = 0; i < count; i++) {
          const item = figures.nth(i);
          await item.scrollIntoViewIfNeeded();
          await item.locator('img').evaluate(image => image.decode());
          const state = await item.evaluate(figure => {
            const image = figure.querySelector('img');
            const rect = figure.getBoundingClientRect();
            return {src: image.getAttribute('src'), natural: image.naturalWidth,
              width: image.clientWidth, left: rect.left, right: rect.right, viewport: innerWidth};
          });
          assert(state.src.endsWith('.svg'));
          assert(state.natural > 0 && state.width > 0);
          assert(state.left >= -1 && state.right <= state.viewport + 1, JSON.stringify(state));
        }
        if (route.startsWith('manuscript')) {
          const selected = page.locator('#figure-2');
          await selected.scrollIntoViewIfNeeded();
          await selected.screenshot({path: path.join(output, `${size.name}-figure2.png`)});
          if (size.name === 'desktop') {
            await page.locator('#figure-1').screenshot({path: path.join(output, 'desktop-figure1.png')});
            await page.locator('#figure-4').screenshot({path: path.join(output, 'desktop-figure4.png')});
          }
          const enlarge = selected.locator('.figure-enlarge');
          await enlarge.click();
          await page.locator('dialog[open] .viewer-artwork').evaluate(image => image.decode());
          const fit = await page.locator('.viewer-viewport').evaluate(view => {
            const image = view.querySelector('img');
            return {width: image.clientWidth, height: image.clientHeight, availableWidth: view.clientWidth, availableHeight: view.clientHeight};
          });
          assert(fit.width <= fit.availableWidth && fit.height <= fit.availableHeight);
          await page.screenshot({path: path.join(output, `${size.name}-viewer-fit.png`)});
          await page.locator('button[data-scale="2"]').click();
          assert.equal(await page.locator('button[data-scale="2"]').getAttribute('aria-pressed'), 'true');
          const zoom = await page.locator('.viewer-viewport').evaluate(view => ({scroll: view.scrollWidth, visible: view.clientWidth, image: view.querySelector('img').clientWidth}));
          assert(zoom.image >= 2240 && zoom.scroll > zoom.visible);
          await page.keyboard.press('Escape');
          assert.equal(await page.locator('dialog[open]').count(), 0);
          assert(await enlarge.evaluate(link => link === document.activeElement));
          await enlarge.click();
          await page.locator('.viewer-close').click();
          assert.equal(await page.locator('dialog[open]').count(), 0);
          await page.emulateMedia({media: 'print'});
          assert.equal(await selected.locator('.figure-toolbar').evaluate(el => getComputedStyle(el).display), 'none');
          await page.emulateMedia({media: 'screen'});
        }
        checks.push({viewport: size.name, route, figures: count, svg_images_loaded: true, figure_widths_fit: true});
      }
      await context.close();
    }
    const nojs = await browser.newContext({javaScriptEnabled: false});
    const page = await nojs.newPage();
    await page.goto(base + 'manuscript/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.html');
    const link = page.locator('#figure-2 .figure-enlarge');
    await link.click();
    assert(page.url().endsWith('/figure2_fact_signal.svg'));
    await nojs.close();
    assert.deepEqual(errors, []);
    const report = {base, checks, keyboard_escape_and_focus_restore: true, zoom_200_percent: true,
      fit_to_viewport: true, print_controls_hidden: true, no_javascript_svg_fallback: true, javascript_errors: errors};
    await fs.writeFile(path.join(output, 'browser_qa.json'), JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify(report, null, 2));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
