import { chromium } from 'playwright';
const BASE='http://127.0.0.1:3100';
const DIR='/home/runner/work/alexandria/alexandria/docs/design/reviews/2026-09-18/orders';
const b=await chromium.launch();
const ctx=await b.newContext({viewport:{width:1440,height:900},deviceScaleFactor:1});
await ctx.addCookies([{name:'__clerk_db_jwt',value:'dvb_2abcdefghijklmnop',domain:'127.0.0.1',path:'/'}]);
const p=await ctx.newPage();
await p.route('**://*.clerk.accounts.dev/**',r=>r.abort());

// disclosure, closed then open
await p.goto(BASE+'/skills'); await p.waitForTimeout(700);
await p.locator('.skill-row').first().scrollIntoViewIfNeeded();
await p.locator('.skill-row-more').first().screenshot({path:`${DIR}/refine-disclosure-closed-after.png`});
await p.locator('.skill-row-more summary').first().click();
await p.waitForTimeout(150);
await p.locator('.skill-row-more').first().screenshot({path:`${DIR}/refine-disclosure-midopen-after.png`});
await p.waitForTimeout(600);
await p.locator('.skill-row-more').first().screenshot({path:`${DIR}/refine-disclosure-open-after.png`});
console.log('marker rotation:', await p.evaluate(()=>getComputedStyle(document.querySelector('.skill-row-more details[open] > summary'),'::after').transform));
console.log('closed marker  :', await p.evaluate(()=>getComputedStyle(document.querySelector('.skill-row-more details:not([open]) > summary'),'::after').transform));

// issue row, resting then hovered
await p.goto(BASE+'/library'); await p.waitForTimeout(800);
for(let i=0;i<5;i++){await p.mouse.wheel(0,220);await p.waitForTimeout(160);} await p.waitForTimeout(3000);
await p.locator('.issue').first().screenshot({path:`${DIR}/refine-issue-rest-after.png`});
await p.locator('.issue h2').first().hover();
await p.waitForTimeout(600);
await p.locator('.issue').first().screenshot({path:`${DIR}/refine-issue-hover-after.png`});
console.log('hovered row shift:', await p.evaluate(()=>getComputedStyle(document.querySelector('.issue h2')).transform));

// reduced motion holds
const ctx2=await b.newContext({viewport:{width:1440,height:900},deviceScaleFactor:1,reducedMotion:'reduce'});
await ctx2.addCookies([{name:'__clerk_db_jwt',value:'dvb_2abcdefghijklmnop',domain:'127.0.0.1',path:'/'}]);
const q=await ctx2.newPage(); await q.route('**://*.clerk.accounts.dev/**',r=>r.abort());
await q.goto(BASE+'/skills'); await q.waitForTimeout(600);
console.log('reduced-motion summary transition:', await q.evaluate(()=>getComputedStyle(document.querySelector('.skill-row-more summary'),'::after').transitionDuration));
await b.close();
