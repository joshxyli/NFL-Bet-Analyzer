// Re-project every saved prop row (weeks 5-12) from as-of stats with tunable weights; grade with the backtest's selection rule.
const fs=require('fs'),path=require('path');const W=__dirname,ASOF=process.argv[2],NFLD=process.argv[3],MODE=process.argv[4]||'cv';
const P0={dec:0.88,prior:0.5,blend:0.7,kcr:15,kypr:10,kypc:40,kypa:100,script:1,def:1,cal:1,sdw:4};globalThis.__P={...P0};
const PM=require(W+'/pm_param.js'),nn=PM.normName;const I=JSON.parse(fs.readFileSync(W+'/tune_in.json','utf8'));const res=new Map(Object.entries(I.results));
const grp=new Map(JSON.parse(fs.readFileSync(W+'/tune_rows.json','utf8')).map(r=>[r.pk,r.g]));
// nflverse schedule for context
const csv=fs.readFileSync(NFLD+'/games.csv','utf8').trim().split('\n');const H=csv[0].split(',');const GM=new Map();
for(const l of csv.slice(1)){const v=l.split(',');const g=Object.fromEntries(H.map((h,i)=>[h,v[i]]));if(g.season==='2026'&&g.game_type==='REG')GM.set(g.away_team+'-'+g.home_team+'-'+g.gameday.replace(/-/g,''),g);}
const stats={};for(let w=4;w<=11;w++){const s=JSON.parse(fs.readFileSync(`${ASOF}/stats_w${w}.json`,'utf8'));s.byName=new Map();for(const p of s.players){const k=nn(p.n)+'|'+p.t;s.byName.set(k,p);if(!s.byName.has(nn(p.n)))s.byName.set(nn(p.n),p);}stats[w]=s;}
const SH=new Set(['player_receptions','player_reception_yds','player_rush_yds']);
const rows=[];let nf=0,np=0,ratios=[];
for(const {doc,key,wk} of I.logs){const r=res.get(key);const g=GM.get(key)||[...GM.values()].find(x=>key.startsWith(x.away_team+'-'+x.home_team));const st=stats[wk-1];
  const players=new Map((r.p||[]).map(s=>{const p=String(s).split('|');return [nn(p[0]),p.map((v,i)=>(i>2?Number(v):v))];}));
  for(const [oi,s] of doc.o.entries()){const f=s.split('|');if(f.length<9||f[0]==='GAME'||!PM.MARKETS[f[1]]||f[6]===''||f[8]==='')continue;
    const o={pl:f[0],m:f[1],s:f[3],pt:+f[4],name:f[10]||''};const out=PM.settle(o,r,players);if(out==='v')continue;
    const box=players.get(nn(f[10]||f[0]))||players.get(nn(f[0]));const team=box?box[1]:null;
    const pl=(team&&st.byName.get(nn(f[10]||f[0])+'|'+team))||st.byName.get(nn(f[10]||f[0]))||st.byName.get(nn(f[0]));
    const pk=doc.eventId+'|'+nn(f[0])+'|'+f[1];const gname=grp.get(pk)||'other';
    const row={ei:doc.eventId,oi,wk,game:key,pk,g:gname,m:f[1],side:f[3],pt:+f[4],pr:+f[5],fair:+f[7],saved:f[3]==='Over'?+f[6]:1-+f[6],mean:Math.max(+f[8],0.05),out,dec:(+f[5]>0?1+ +f[5]/100:1+100/-+f[5])};
    if(pl&&g){const home=pl.t===g.home_team,opp=home?g.away_team:g.home_team;const sp=g.spread_line===''||g.spread_line==='NA'?null:+g.spread_line;
      const roof=g.roof||'retractable';row.pl=pl;row.st=st;
      row.ctx={opp,home:g.location==='Neutral'?null:home,fav:sp==null?null:(home?sp:-sp),total:g.total_line===''||g.total_line==='NA'?null:+g.total_line,indoor:['dome','closed','retractable'].includes(roof),wind:(g.wind===''||g.wind==='NA')?null:+g.wind};
      globalThis.__P={...P0};const p0=PM.project(pl,f[1],row.ctx,st);if(p0&&p0.mean>0){row.p0=p0;ratios.push(p0.mean/row.mean);row.c0=chance(row,p0);}else np++;}else nf++;
    rows.push(row);}}
function chance(row,pj){ // over chance from a projection, scaled to the saved mean
  const k=row.mean/row.p0.mean,mu=pj.mean*k;
  if(['WR1/2','WR3+','RB1','RB2+'].includes(row.g)&&SH.has(row.m)&&!(row.g.startsWith('WR')&&row.m==='player_rush_yds'))
    return PM.sideProbs({mean:Math.max(mu,0.05),sd:1,shape:{pos:row.g.slice(0,2),low:(row.g==='WR3+'||row.g==='RB2+')?1:0}},row.m,row.pt).over;
  const q={mean:mu,sd:pj.sd==null?null:pj.sd*k,shape:null};
  return (PM.isThin(q,row.m,row.pt)?PM.empirical(row.pl,row.m,row.pt):PM.sideProbs(q,row.m,row.pt)).over;}
ratios.sort((a,b)=>a-b);const q=x=>ratios[Math.floor(x*ratios.length)];
console.error(`rows ${rows.length}; re-projected ${ratios.length}; player not in as-of stats ${nf}; no projection ${np}`);
console.error(`rebuilt projection / saved projection: median ${q(.5).toFixed(3)}, 10-90% ${q(.1).toFixed(3)}-${q(.9).toFixed(3)}, within 10%: ${(ratios.filter(x=>Math.abs(x-1)<0.1).length/ratios.length).toFixed(2)}`);
const T=[0.1,0.2,0.3,0.6,1.0],WKS=[5,6,7,8,9,10,11];
function evalP(P,rule){globalThis.__P=P;const same=JSON.stringify(P)===JSON.stringify(P0);const prof={};
  const best=new Map();
  for(const r of rows){let ov=r.saved; // over-side chance for this row's side
    if(r.shaped)ov=r.c0;                                   // WR/RB shape rows: current shape from the saved projection (exact for weeks 10+)
    if(r.p0&&!same){const pj=PM.project(r.pl,r.m,r.ctx,r.st);if(pj&&pj.mean>0){const c=chance(r,pj);ov=r.shaped?c:r.saved+(c-r.c0);}}
    let m=r.side==='Over'?ov:1-ov;m=Math.min(0.999,Math.max(0.001,m));if(r.side!=='Over')m=Math.min(0.999,Math.max(0.001,1-ov));
    if(r.side==='Over')m=Math.min(0.999,Math.max(0.001,ov));
    if(rule&&(r.g==='WR1/2'||r.g==='WR3+'||r.g==='RB2+'))m=r.fair;
    for(const w of T){const p=w*m+(1-w)*r.fair,ev=p*r.dec-1,k=r.pk+'|'+w,c=best.get(k);if(!c||ev>c.ev)best.set(k,{ev,e:p-1/r.dec,r,w});}}
  for(const c of best.values()){if(c.e<=0||c.r.out==='p')continue;const k=c.r.wk+'|'+c.w;prof[k]=(prof[k]||0)+(c.r.out==='w'?c.r.dec-1:-1);prof['n'+k]=(prof['n'+k]||0)+1;}
  return prof;}
// note: r.saved is the chance of the row's own side, so turn it into the over chance once
for(const r of rows){r.shaped=['WR1/2','WR3+','RB1','RB2+'].includes(r.g)&&SH.has(r.m)&&!(r.g.startsWith('WR')&&r.m==='player_rush_yds')&&r.c0!=null;}
// check: weeks 10-12 saved chances are the current model, so the rebuilt shape chance must equal them
{const d=rows.filter(r=>r.shaped&&r.wk>=10).map(r=>Math.abs(r.c0-r.saved)).sort((a,b)=>a-b);console.error('weeks 10-12 shape rows, rebuilt vs saved |diff|: median',d[d.length>>1].toFixed(4),'90th',d[Math.floor(d.length*.9)].toFixed(4));}
const GRID={dec:[0.75,0.8,0.85,0.88,0.92,0.96,1],prior:[0,0.25,0.5,0.75,1],blend:[0.3,0.5,0.6,0.7,0.8,0.9,1],kcr:[5,15,30,60],kypr:[3,10,25,50],kypc:[10,40,100],kypa:[30,100,300],script:[0,0.5,1,1.5],def:[0,0.5,1,1.5,2],cal:[0,0.5,1,1.5],sdw:[1,4,10]};
const cache=new Map();const ev=(P,rule)=>{const k=JSON.stringify(P)+rule;if(!cache.has(k))cache.set(k,evalP(P,rule));return cache.get(k);};
const score=(pr,wks,ts=T)=>wks.reduce((a,wk)=>a+ts.reduce((b,w)=>b+(pr[wk+'|'+w]||0),0),0);
function fit(wks,rule){let P={...P0},best=score(ev(P,rule),wks);
  for(let pass=0;pass<2;pass++)for(const [k,vals] of Object.entries(GRID)){for(const v of vals){const Q={...P,[k]:v};const s=score(ev(Q,rule),wks);if(s>best+1e-9){best=s;P=Q;}}}
  return {P,best};}

if(MODE==='dump'){const CFG=JSON.parse(process.env.CFGS);const out={};
  for(const [name,P,rule] of CFG){const Q={...P0,...P};globalThis.__P=Q;const same=JSON.stringify(Q)===JSON.stringify(P0);const m={};
    for(const r of rows){let ov=r.saved;if(r.shaped)ov=r.c0;if(r.p0&&!same){const pj=PM.project(r.pl,r.m,r.ctx,r.st);if(pj&&pj.mean>0){const c=chance(r,pj);ov=r.shaped?c:r.saved+(c-r.c0);}}
      let side=Math.min(0.999,Math.max(0.001,r.side==='Over'?ov:1-ov));if(rule&&(r.g==='WR1/2'||r.g==='WR3+'||r.g==='RB2+'))side=r.fair;m[r.ei+'|'+r.oi]=side;}
    out[name]=m;}
  fs.writeFileSync(W+'/proj_dump.json',JSON.stringify(out));console.error('dump done');process.exit(0);}
if(MODE==='eval'){
  const CFG=JSON.parse(process.env.CFGS);const res={};
  function perGame(P,rule,w){globalThis.__P=P;const same=JSON.stringify(P)===JSON.stringify(P0);const best=new Map();
    for(const r of rows){let ov=r.saved;if(r.shaped)ov=r.c0;
      if(r.p0&&!same){const pj=PM.project(r.pl,r.m,r.ctx,r.st);if(pj&&pj.mean>0){const c=chance(r,pj);ov=r.shaped?c:r.saved+(c-r.c0);}}
      let m=Math.min(0.999,Math.max(0.001,r.side==='Over'?ov:1-ov));if(rule&&(r.g==='WR1/2'||r.g==='WR3+'||r.g==='RB2+'))m=r.fair;
      const p=w*m+(1-w)*r.fair,ev=p*r.dec-1,c=best.get(r.pk);if(!c||ev>c.ev)best.set(r.pk,{ev,e:p-1/r.dec,r});}
    const g={};for(const c of best.values()){if(c.e<=0||c.r.out==='p')continue;const k=c.r.wk+'|'+c.r.game;g[k]=g[k]||[0,0];g[k][0]+=c.r.out==='w'?c.r.dec-1:-1;g[k][1]++;}return g;}
  for(const [name,P,rule] of CFG)for(const w of T)res[name+'|'+w]=perGame({...P0,...P},rule,w);
  fs.writeFileSync(W+'/proj_eval_out.json',JSON.stringify(res));console.error('eval done');process.exit(0);}
const OUT={};
for(const rule of [false,true]){const tag=rule?'with WR/RB2+ rule':'no rule';const base=ev(P0,rule);
  const cv={},cur={};let folds=[];
  for(const h of WKS){const tr=WKS.filter(x=>x!==h);const {P}=fit(tr,rule);const pr=ev(P,rule);for(const w of T){cv[w]=(cv[w]||0)+(pr[h+'|'+w]||0);cur[w]=(cur[w]||0)+(base[h+'|'+w]||0);}folds.push([h,Object.entries(P).filter(([k,v])=>v!==P0[k]).map(([k,v])=>k+'='+v).join(' ')]);}
  const {P}=fit(WKS,rule);const fin=ev(P,rule);
  OUT[tag]={cv,cur,folds,final:P,inSample:Object.fromEntries(T.map(w=>[w,[+score(fin,WKS,[w]).toFixed(1),WKS.reduce((a,wk)=>a+(fin['n'+wk+'|'+w]||0),0)]])),curIn:Object.fromEntries(T.map(w=>[w,[+score(base,WKS,[w]).toFixed(1),WKS.reduce((a,wk)=>a+(base['n'+wk+'|'+w]||0),0)]])),
    wk12:Object.fromEntries(T.map(w=>[w,[+score(fin,[12],[w]).toFixed(1),+score(base,[12],[w]).toFixed(1)]]))};
  console.error('done',tag);}
fs.writeFileSync(W+'/proj_tune_out.json',JSON.stringify(OUT,null,1));
