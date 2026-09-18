import { chromium } from 'playwright';
const BASE='http://127.0.0.1:3100';
const b=await chromium.launch();
const PAGES=[['home','/'],['library','/library'],['skills','/skills'],['pricing','/pricing'],['mission','/mission'],['routines','/routines'],['404','/nope']];
for (const [vp,w,h,touch] of [['iphone',390,844,true],['ipad',820,1180,true],['desktop',1440,900,false]]) {
  const ctx=await b.newContext({viewport:{width:w,height:h},deviceScaleFactor:1,hasTouch:touch,isMobile:touch});
  await ctx.addCookies([{name:'__clerk_db_jwt',value:'dvb_2abcdefghijklmnop',domain:'127.0.0.1',path:'/'}]);
  const p=await ctx.newPage();
  await p.route('**://*.clerk.accounts.dev/**',r=>r.abort());
  for (const [name,path] of PAGES){
    await p.goto(BASE+path,{waitUntil:'load'}); await p.waitForTimeout(700);
    const tight=await p.evaluate(()=>{
      const out=[];
      const label=(el)=>el.tagName.toLowerCase()+(el.className&&typeof el.className==='string'?'.'+el.className.trim().split(/\s+/).join('.'):'');
      const walk=(parent)=>{
        const kids=[...parent.children].filter(el=>{
          const cs=getComputedStyle(el);
          if(cs.display==='none'||cs.visibility==='hidden'||el.hidden) return false;
          const r=el.getBoundingClientRect();
          return r.height>0 && r.width>0;
        });
        for(let i=1;i<kids.length;i++){
          const a=kids[i-1].getBoundingClientRect(), c=kids[i].getBoundingClientRect();
          if(c.top<a.bottom-1) continue;           // overlapping or inline row
          if(Math.abs(c.top-a.top)<4) continue;     // side by side
          const gap=Math.round(c.top-a.bottom);
          if(gap>=0 && gap<16) out.push({gap,after:label(kids[i-1]).slice(0,44),before:label(kids[i]).slice(0,44)});
        }
        for(const k of kids) if(k.children.length>1) walk(k);
      };
      walk(document.body);
      return out.sort((x,y)=>x.gap-y.gap).slice(0,7);
    });
    if(tight.length) console.log(`\n${vp} ${name}:`), tight.forEach(t=>console.log(`   ${String(t.gap).padStart(3)}px  ${t.after}  ->  ${t.before}`));
  }
  await ctx.close();
}
await b.close();
