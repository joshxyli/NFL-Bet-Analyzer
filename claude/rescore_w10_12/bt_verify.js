// Runs the published app's own PM.backtest on saved lines under each proposed change; per-game output so totals can be bootstrapped.
const fs=require('fs');const CUR=require(__dirname+'/pm_new.js');const RBH=require(__dirname+'/pm_v_rbrec.js');
const I=JSON.parse(fs.readFileSync(__dirname+'/bt_docs.json','utf8'));const res=new Map(Object.entries(I.results));
const nn=CUR.normName, SH=new Set(['player_receptions','player_reception_yds','player_rush_yds']);
function groups(entries){ // shape group per (event|player), read off the saved chance, fallback depth chart
  const vote=new Map(), pos=new Map();
  for(const {doc,key} of entries){const r=res.get(key);const box=new Map((r.p||[]).map(s=>{const p=s.split('|');return [nn(p[0]),p];}));
    for(const s of doc.o){const f=s.split('|');if(f[0]==='GAME'||!SH.has(f[1])||f[6]===''||f[8]==='')continue;const b=box.get(nn(f[10]||f[0]))||box.get(nn(f[0]));if(!b)continue;
      const P=b[2];if(P!=='WR'&&P!=='RB')continue;const k=doc.eventId+'|'+nn(f[0]);pos.set(k,[P,b[1],nn(b[0])]);if(P==='WR'&&f[1]==='player_rush_yds')continue;
      const pt=Number(f[4]),mu=Math.max(Number(f[8]),0.05),sv=f[3]==='Over'?Number(f[6]):1-Number(f[6]);
      const o0=CUR.sideProbs({mean:mu,sd:mu*.6,shape:{pos:P,low:0}},f[1],pt).over,o1=CUR.sideProbs({mean:mu,sd:mu*.6,shape:{pos:P,low:1}},f[1],pt).over;
      if(Math.abs(o0-o1)>0.004){const v=vote.get(k)||[0,0];v[Math.abs(sv-o0)<Math.abs(sv-o1)?0:1]++;vote.set(k,v);}}}
  const G=new Map();let fb=0;
  for(const [k,[P,t,n]] of pos){const v=vote.get(k);let low;if(v)low=v[1]>v[0]?1:0;else{fb++;const d=I.dr[n+'|'+t]||'';low=/^(WR[12]|RB1)$/.test(d)?0:1;}
    G.set(k,P+(low?'low':'top'));}
  return {G,fb};
}
function variant(entries,G,name){ // returns modified copies of the docs
  return entries.map(({doc,key})=>{const d={...doc,o:doc.o.map(s=>{const f=s.split('|');if(f[0]==='GAME'||f.length<8||f[6]==='')return s;const g=G.get(doc.eventId+'|'+nn(f[0]));
    if(name==='marketOnly'){f[6]=f[7];return f.join('|');}
    if(name==='offWR_RB2'&&g&&(g.startsWith('WR')||g==='RBlow')){f[6]=f[7];return f.join('|');}
    if(name==='rbRecHalf'&&g==='RBlow'&&f[1]==='player_reception_yds'&&f[8]!==''){const mu=Math.max(Number(f[8]),0.05),o=RBH.sideProbs({mean:mu,sd:mu*.6,shape:{pos:'RB',low:1}},f[1],Number(f[4])).over;f[6]=(f[3]==='Over'?o:1-o).toFixed(4);return f.join('|');}
    return s;})};return {doc:d,key};});
}
const OUT={};
for(const [per,entries] of Object.entries(I.periods)){
  const {G,fb}=groups(entries);OUT[per]={fallback:fb,games:entries.length,runs:{}};
  for(const vname of ['current','rbRecHalf','offWR_RB2','marketOnly']){const docs=variant(entries,G,vname);
    for(const be of [0,0.5425,0.5774]) for(const w of [0.1,0.3,0.6,1.0]){
      if(vname==='marketOnly'&&w!==1.0)continue;  // trust has no effect when model = market
      const per_game=docs.map(({doc,key})=>{const bt=CUR.backtest([doc],res,{keyOf:()=>key,abbr:n=>n,w,gw:0.3,be});
        return [key,bt.bet.props.map(b=>[b.bets,b.w,+b.profit.toFixed(4)])];});
      OUT[per].runs[`${vname}|be=${be}|w=${w}`]=per_game;}}
}
fs.writeFileSync(__dirname+'/bt_verify_out.json',JSON.stringify(OUT));console.log('done',Object.fromEntries(Object.entries(OUT).map(([k,v])=>[k,{games:v.games,fallback:v.fallback}])));
