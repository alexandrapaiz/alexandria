import { chromium } from 'playwright';
const b=await chromium.launch();
for (const [vp,w,h,touch] of [['iphone',390,844,true],['ipad',820,1180,true],['desktop',1440,900,false]]) {
  const ctx=await b.newContext({viewport:{width:w,height:h},deviceScaleFactor:1,hasTouch:touch,isMobile:touch});
  await ctx.addCookies([{name:'__clerk_db_jwt',value:'dvb_2abcdefghijklmnop',domain:'127.0.0.1',path:'/'}]);
  const p=await ctx.newPage();
  await p.route('**://*.clerk.accounts.dev/**',r=>r.abort());
  await p.goto('http://127.0.0.1:3100/pricing',{waitUntil:'load'}); await p.waitForTimeout(600);
  const r=await p.evaluate(()=>{
    const g=(a,b2)=>{const A=document.querySelector(a),B=document.querySelector(b2);
      if(!A||!B) return null; return Math.round(B.getBoundingClientRect().top-A.getBoundingClientRect().bottom);};
    const cs=(s,prop)=>getComputedStyle(document.querySelector(s))[prop];
    return {
      introToTiers:g('.page-intro','.tiers'),
      tierGap:g('.tier',' .tier.featured'),
      tiersToWaitlist:g('.tiers','.waitlist-block'),
      waitlistToBilling:g('.waitlist-block','.billing-note'),
      tiersCols:cs('.tiers','gridTemplateColumns'),
      tierPad:cs('.tier','padding'),
      pagePad:cs('.page','padding'),
      priceToPer:g('.tier .price','.tier .per'),
      perToUl:g('.tier .per','.tier ul'),
      liGap:(()=>{const li=[...document.querySelectorAll('.tier ul li')];return li.length>1?Math.round(li[1].getBoundingClientRect().top-li[0].getBoundingClientRect().bottom):null;})(),
    };
  });
  console.log(vp, JSON.stringify(r));
  await ctx.close();
}
await b.close();
