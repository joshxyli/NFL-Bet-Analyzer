// App's own PM.backtest on the saved weeks 5-12 lines: current model vs "model off for WR1/2, WR3+, RB2+" (model chance := market there)
const fs=require('fs');const PM=require(__dirname+'/pm_new.js');const I=JSON.parse(fs.readFileSync(__dirname+'/tune_in.json','utf8'));
const res=new Map(Object.entries(I.results));const nn=PM.normName;const SH=new Set(['player_receptions','player_reception_yds','player_rush_yds']);
const R=JSON.parse(fs.readFileSync(__dirname+'/tune_rows.json','utf8'));const grp=new Map();for(const r of R){grp.set(r.pk.split('|').slice(0,2).join('|'),r.g);}
function build(off){return I.logs.map(({doc,key,wk})=>{const r=res.get(key);const box=new Map((r.p||[]).map(s=>{const p=s.split('|');return [nn(p[0]),p];}));
  const o=doc.o.map(s=>{const f=s.split('|');if(f.length<8||f[0]==='GAME'||f[6]==='')return s;const g=grp.get(doc.eventId+'|'+nn(f[0]));
    if(wk<10&&SH.has(f[1])&&f[8]!==''&&g&&(g!=='WR1/2'&&g!=='WR3+'||f[1]!=='player_rush_yds')&&(g.startsWith('WR')||g.startsWith('RB'))){ // weeks 5-9 were saved under the old shape: rebuild with the current one
      const low=(g==='WR3+'||g==='RB2+')?1:0,mu=Math.max(+f[8],0.05),ov=PM.sideProbs({mean:mu,sd:1,shape:{pos:g.slice(0,2),low}},f[1],+f[4]).over;f[6]=(f[3]==='Over'?ov:1-ov).toFixed(4);}
    if(off&&g&&(g==='WR1/2'||g==='WR3+'||g==='RB2+'))f[6]=f[7];
    return f.join('|');});return {doc:{...doc,o},key,wk};});}
const out={};
for(const [name,off] of [['current',false],['rule',true]]){const E=build(off);
  for(const [lab,ws] of [['wk5-11',[5,6,7,8,9,10,11]],['wk12',[12]]]){const S=E.filter(e=>ws.includes(e.wk));const km=new Map(S.map(e=>[e.doc.eventId,e.key]));
    for(const w of [0.1,0.2,0.3,0.6,1.0]){const bt=PM.backtest(S.map(e=>e.doc),res,{keyOf:d=>km.get(d.eventId),abbr:n=>n,w,gw:0.3,be:0});
      const b=bt.bet.props;out[`${name}|${lab}|${w}`]=b.map(x=>[x.label,x.bets,x.w,+x.profit.toFixed(1)]);}}}
for(const lab of ['wk5-11','wk12'])for(const w of [0.1,0.2,0.3,0.6,1.0]){const c=out[`current|${lab}|${w}`],r=out[`rule|${lab}|${w}`];
  const f=x=>`${x[1]} bets ${x[2]}W ${x[3]>=0?'+':''}${x[3]}u (${x[1]?(100*x[3]/x[1]).toFixed(1):0}%)`;
  console.log(`${lab} trust ${w*100}%  positive edge: current ${f(c[1])} | rule ${f(r[1])}   ;  every pick: current ${c[0][3]}u rule ${r[0][3]}u`);}
