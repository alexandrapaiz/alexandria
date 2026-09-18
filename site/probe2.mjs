import { chromium } from 'playwright';
const b=await chromium.launch();
for (const [vp,w,h,touch] of [['iphone',390,844,true],['ipad',820,1180,true],['desktop',1440,900,false]]) {
  const ctx=await b.newContext({viewport:{width:w,height:h},deviceScaleFactor:1,hasTouch:touch,isMobile:touch});
  await ctx.addCookies([{name:'__clerk_db_jwt',value:'dvb_2abcdefghijklmnop',domain:'127.0.0.1',path:'/'}]);
  const p=await ctx.newPage();
  await p.route('**://*.clerk.accounts.dev/**',r=>r.abort());
  const g=(a,b2)=>`(()=>{const A=document.querySelector('${a}'),B=document.querySelector('${b2}');return A&&B?Math.round(B.getBoundingClientRect().top-A.getBoundingClientRect().bottom):null})()`;

  await p.goto('http://127.0.0.1:3100/',{waitUntil:'load'}); await p.waitForTimeout(700);
  for(let i=0;i<10;i++){await p.mouse.wheel(0,400);await p.waitForTimeout(180);} await p.waitForTimeout(1200);
  const home=await p.evaluate(`({
    statementToAct: ${g('.statement','.hero-act')},
    actToAbout: ${g('.hero-act','.about-inline')},
    aboutToFooter: ${g('.about-inline','.footer')},
    heroFollowPad: getComputedStyle(document.querySelector('.hero-follow')).padding,
    waitlistNote: ${g('.waitlist','.waitlist-note')},
    pillGap: getComputedStyle(document.querySelector('.hero-act')).gap
  })`);
  console.log(vp,'home',JSON.stringify(home));

  await p.goto('http://127.0.0.1:3100/routines',{waitUntil:'load'}); await p.waitForTimeout(500);
  const rt=await p.evaluate(`({
    introToGate: ${g('.page-intro','.gate')},
    h3ToP: ${g('.gate h3','.gate p')},
    pToPill: ${g('.gate p','.gate .pill')},
    gateAlign: getComputedStyle(document.querySelector('.gate')).textAlign
  })`);
  console.log(vp,'routines',JSON.stringify(rt));
  await ctx.close();
}
await b.close();
