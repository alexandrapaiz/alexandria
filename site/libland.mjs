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
  await p.goto(BASE+'/library',{waitUntil:'load'});
  await p.waitForTimeout(1000);
  for (let i=0;i<4;i++){ await p.mouse.wheel(0,220); await p.waitForTimeout(160); }
  await p.waitForTimeout(3500);
  await p.screenshot({path:`${DIR}/library-land-${vp}-${phase}.png`});
  const m=await p.evaluate(()=>{
    const nav=document.querySelector('.nav').getBoundingClientRect();
    const k=document.querySelector('.lib-scene2 .page-kicker').getBoundingClientRect();
    const t=document.querySelector('.lib-scene2 .page-title').getBoundingClientRect();
    return {scrollY:window.scrollY, navBottom:Math.round(nav.bottom), kickerTop:Math.round(k.top), titleTop:Math.round(t.top)};
  });
  console.log(vp, JSON.stringify(m));
  await ctx.close();
}
await b.close();
