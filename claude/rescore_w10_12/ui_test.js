// Browser test of the edited page in website mode. The page and its data files are served from disk by Playwright's
// request routing (no server process). usage: node ui_test.js <desktop.png> <phone.png> <site dir>
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const SITE = process.argv[4];
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1300, height: 1000 } });
  const errs = []; pg.on('pageerror', (e) => errs.push(e.message)); pg.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  await pg.route('http://app.test/**', (r) => {
    const u = new URL(r.request().url()); const f = SITE + '/' + (u.pathname.slice(1) || 'index.html');
    if (!fs.existsSync(f)) return r.fulfill({ status: 404, body: '' });
    return r.fulfill({ status: 200, body: fs.readFileSync(f), contentType: f.endsWith('.html') ? 'text/html' : 'application/json' });
  });
  await pg.goto('http://app.test/index.html'); await pg.waitForTimeout(4000);
  const board = async () => pg.$$eval('#board-body tr', (rs) => rs.filter((r) => r.querySelector('.c-edge')).slice(0, 4).map((r) => [r.querySelector('.pname')?.textContent.trim().slice(0, 22), r.querySelector('.c-pick')?.textContent.trim().slice(0, 28), r.querySelector('.c-edge')?.textContent.trim().slice(0, 40)]));
  const nrows = async () => pg.$$eval('#board-body tr', (rs) => rs.filter((r) => r.querySelector('.c-edge')).length);
  const posEdge = async () => pg.$$eval('#board-body .c-edge .pill.good', (x) => x.length);
  console.log('controls present:', !!(await pg.$('#f-pricing')), !!(await pg.$('#f-lowq')), '| default pricing', await pg.$eval('#f-pricing', (e) => e.value), '| quarter ticked', await pg.$eval('#f-lowq', (e) => e.checked));
  for (const mode of ['pe2', 'pe4', 'book']) {
    await pg.selectOption('#f-pricing', mode); await pg.waitForTimeout(800);
    console.log(`board ${mode}: rows ${await nrows()}, positive-edge pills ${await posEdge()}`, JSON.stringify(await board()));
  }
  await pg.selectOption('#f-pricing', 'pe2'); await pg.click('#f-lowq'); await pg.waitForTimeout(800);
  console.log('board pe2, quarter weight OFF: positive-edge pills', await posEdge(), '| ticked now', await pg.$eval('#f-lowq', (e) => e.checked));
  await pg.click('#f-lowq'); await pg.waitForTimeout(500);
  const bt = async () => pg.$$eval('#bt-bets tr', (rs) => rs.slice(0, 3).map((r) => r.textContent.replace(/\s+/g, ' ').trim()));
  for (const mode of ['pe2', 'pe4', 'book']) {
    await pg.click('#tab-board'); await pg.selectOption('#f-pricing', mode); await pg.click('#tab-backtest'); await pg.waitForTimeout(1500);
    console.log(`backtest ${mode}:`, JSON.stringify(await bt()));
  }
  await pg.click('#tab-board'); await pg.selectOption('#f-pricing', 'pe2'); await pg.click('#f-lowq'); await pg.click('#tab-backtest'); await pg.waitForTimeout(1500);
  console.log('backtest pe2, quarter OFF:', JSON.stringify(await bt()));
  await pg.reload(); await pg.waitForTimeout(3500);
  console.log('after reload: pricing', await pg.$eval('#f-pricing', (e) => e.value), '| quarter ticked', await pg.$eval('#f-lowq', (e) => e.checked));
  await pg.click('#tab-board'); await pg.waitForTimeout(500); await pg.screenshot({ path: process.argv[2], clip: { x: 0, y: 0, width: 1300, height: 700 } });
  await pg.setViewportSize({ width: 390, height: 900 }); await pg.waitForTimeout(500); await pg.screenshot({ path: process.argv[3] });
  console.log('page errors:', errs.length ? errs : 'none'); await b.close();
})();
