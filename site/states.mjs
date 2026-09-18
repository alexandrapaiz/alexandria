import { chromium } from 'playwright';
const BASE = 'http://127.0.0.1:3100';
const DIR = '/home/runner/work/alexandria/alexandria/docs/design/reviews/2026-09-18/copy';
const b = await chromium.launch();

for (const [vp, w, h, touch] of [['iphone',390,844,true],['desktop',1440,900,false]]) {
  const ctx = await b.newContext({ viewport:{width:w,height:h}, deviceScaleFactor:1, hasTouch:touch, isMobile:touch });
  await ctx.addCookies([{name:'__clerk_db_jwt',value:'dvb_2abcdefghijklmnop',domain:'127.0.0.1',path:'/'}]);
  const p = await ctx.newPage();
  await p.route('**://*.clerk.accounts.dev/**', r=>r.abort());

  // waitlist: confirmed
  await p.goto(BASE + '/pricing', { waitUntil:'load' });
  await p.waitForTimeout(700);
  await p.locator('#waitlist').scrollIntoViewIfNeeded();
  await p.fill('#waitlist input[type=email]', `copy-run-${vp}@example.com`);
  await p.click('#waitlist button[type=submit]');
  await p.waitForTimeout(1200);
  await p.locator('#waitlist').screenshot({ path:`${DIR}/waitlist-confirmed-${vp}-after.png` });
  console.log('confirmed', vp, await p.locator('.waitlist-done').innerText().catch(()=>'MISSING'));

  // waitlist: rejected
  await p.goto(BASE + '/pricing', { waitUntil:'load' });
  await p.waitForTimeout(700);
  await p.locator('#waitlist').scrollIntoViewIfNeeded();
  await p.fill('#waitlist input[type=email]', 'not-an-address');
  await p.click('#waitlist button[type=submit]');
  await p.waitForTimeout(1200);
  await p.locator('#waitlist').screenshot({ path:`${DIR}/waitlist-invalid-${vp}-after.png` });
  console.log('invalid', vp, await p.locator('.waitlist-note.is-error').innerText().catch(()=>'MISSING'));

  if (touch) {
    // the menu panel, which now carries sign-in
    await p.goto(BASE + '/', { waitUntil:'load' });
    await p.waitForTimeout(700);
    await p.click('.mobile-nav-toggle');
    await p.waitForTimeout(500);
    await p.screenshot({ path:`${DIR}/nav-menu-${vp}-after.png` });
    console.log('menu', await p.locator('.mobile-nav-panel').innerText());
  }
  await ctx.close();
}
await b.close();
console.log('states done');
