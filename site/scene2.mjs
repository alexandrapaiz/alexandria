import { chromium } from 'playwright';
const BASE='http://127.0.0.1:3100';
const phase=process.argv[2]||'before';
const DIR='/home/runner/work/alexandria/alexandria/docs/design/reviews/2026-09-18/orders';
const b=await chromium.launch();
for (const [vp,w,h,touch] of [['iphone',390,844,true],['ipad',820,1180,true],['desktop',1440,900,false]]) {
  const ctx=await b.newContext({viewport:{width:w,height:h},deviceScaleFactor:1,hasTouch:touch,isMobile:touch});
  await ctx.addCookies([{name:'__clerk_db_jwt',value:'dvb_2abcdefghijklmnop',domain:'127.0.0.1',path:'/'}]);
  const p=await ctx.newPage();
  await p.route('**://*.clerk.accounts.dev/**',r=>r.abort());
  await p.goto(BASE+'/',{waitUntil:'load'});
  await p.waitForTimeout(800);
  for (let i=0;i<14;i++){ await p.mouse.wheel(0,400); await p.waitForTimeout(220); }
  await p.waitForTimeout(1200);
  await p.screenshot({path:`${DIR}/home-scene2-${vp}-${phase}.png`});
  const y=await p.evaluate(()=>window.scrollY);
  console.log(vp,'scrollY',y);
  await ctx.close();
}
await b.close();
