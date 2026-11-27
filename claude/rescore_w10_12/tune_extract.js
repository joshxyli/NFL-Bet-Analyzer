// one record per saved prop row: week, game, pick key, group, side, price, fair, model chance (over) for every shape setting, outcome via the app's settle()
const fs=require('fs');const PM=require(__dirname+'/pm_new.js');const I=JSON.parse(fs.readFileSync(__dirname+'/tune_in.json','utf8'));
const res=new Map(Object.entries(I.results));const nn=PM.normName;const SH=new Set(['player_receptions','player_reception_yds','player_rush_yds']);
const src=fs.readFileSync(__dirname+'/pm_new.js','utf8');
// parameterised copy of the app's shape: level for WR1/2, scale on the low-group zero-production term per (pos, market)
const ZW=[-2.164,-0.149,2.253],ZRr=[-1.219,-0.191,1.545],ZRu=[-2.219,-0.025,2.381];
function mkPM(level,zs){let s=src.replace('const WR12_LEVEL = 1.07;','const WR12_LEVEL = '+level+';');
  s=s.replace('z: [-2.164, -0.149, 2.253]','z: [-2.164, -0.149, '+ZW[2]*zs.WR+']').replace('z: [-1.219, -0.191, 1.545]','z: [-1.219, -0.191, '+ZRr[2]*zs.RBrec+']').replace('z: [-2.219, -0.025, 2.381]','z: [-2.219, -0.025, '+ZRu[2]*zs.RBrush+']');
  const p=__dirname+`/pm_t_${level}_${zs.WR}_${zs.RBrec}_${zs.RBrush}.js`;fs.writeFileSync(p,s);return require(p);}
const LEV=[1.0,1.035,1.07],ZS=[0,0.25,0.5,0.75,1];
const V={};for(const l of LEV)for(const z of ZS){V['WR|'+l+'|'+z]=mkPM(l,{WR:z,RBrec:1,RBrush:1});}
for(const z of ZS){V['RBrec|'+z]=mkPM(1.07,{WR:1,RBrec:z,RBrush:1});V['RBrush|'+z]=mkPM(1.07,{WR:1,RBrec:1,RBrush:z});}
// sanity: default settings reproduce the app
const t={mean:40,sd:20,shape:{pos:'WR',low:1}};if(Math.abs(V['WR|1.07|1'].sideProbs(t,'player_reception_yds',30.5).over-PM.sideProbs(t,'player_reception_yds',30.5).over)>1e-12)throw 'default mismatch';
// shape group per event|player: vote from the app's chance (saved for weeks 10+, the re-scored doc for weeks 5-9), else depth chart
const RSC=new Map(Object.entries(I.rescore));const vote=new Map();
function addVote(doc,box){for(const s of doc.o){const f=s.split('|');if(f[0]==='GAME'||!SH.has(f[1])||f[6]===''||f[8]==='')continue;const b=box.get(nn(f[10]||f[0]))||box.get(nn(f[0]));if(!b||(b[2]!=='WR'&&b[2]!=='RB'))continue;if(b[2]==='WR'&&f[1]==='player_rush_yds')continue;
  const mu=Math.max(+f[8],0.05),pt=+f[4],sv=f[3]==='Over'?+f[6]:1-+f[6];const o0=PM.sideProbs({mean:mu,sd:1,shape:{pos:b[2],low:0}},f[1],pt).over,o1=PM.sideProbs({mean:mu,sd:1,shape:{pos:b[2],low:1}},f[1],pt).over;
  if(Math.abs(o0-o1)>0.004){const k=doc.eventId+'|'+nn(f[0]);const v=vote.get(k)||[0,0];v[Math.abs(sv-o0)<Math.abs(sv-o1)?0:1]++;vote.set(k,v);}}}
const out=[];let fb=0;
for(const {doc,key,wk} of I.logs){const r=res.get(key);const box=new Map((r.p||[]).map(s=>{const p=s.split('|');return [nn(p[0]),p];}));
  if(wk>=10)addVote(doc,box);else if(RSC.has(doc.eventId))addVote(RSC.get(doc.eventId),box);
  const players=new Map((r.p||[]).map(s=>{const p=String(s).split('|');return [nn(p[0]),p.map((v,i)=>(i>2?Number(v):v))];}));
  for(const s of doc.o){const f=s.split('|');if(f.length<8||f[0]==='GAME'||!PM.MARKETS[f[1]]||f[6]==='')continue;
    const o={pl:f[0],m:f[1],s:f[3],pt:+f[4],name:f[10]||''};const outc=PM.settle(o,r,players);if(outc==='v')continue;
    const b=box.get(nn(f[10]||f[0]))||box.get(nn(f[0]));const P=b?b[2]:'?';const k=doc.eventId+'|'+nn(f[0]);
    let g=P==='WR'||P==='RB'?null:(P==='QB'||P==='TE'?P:'other');
    const rec={wk,game:key,pk:doc.eventId+'|'+nn(f[0])+'|'+f[1],side:f[3],pr:+f[5],fair:+f[7],out:outc,m:f[1]};
    const sv=f[3]==='Over'?+f[6]:1-+f[6];
    if(g){rec.g=g;rec.p={base:sv};}
    else{const v=vote.get(k);let low;if(v)low=v[1]>v[0]?1:0;else{fb++;const d=I.dr[nn(b[0])+'|'+b[1]]||'';low=/^(WR[12]|RB1)$/.test(d)?0:1;}
      rec.g=P==='WR'?(low?'WR3+':'WR1/2'):(low?'RB2+':'RB1');rec.p={};const mu=Math.max(+f[8],0.05);
      if(P==='WR'&&f[1]==='player_rush_yds'){rec.p.base=sv;}
      else if(P==='WR'){for(const l of LEV)for(const z of ZS)rec.p[l+'|'+z]=V['WR|'+l+'|'+z].sideProbs({mean:mu,sd:1,shape:{pos:'WR',low}},f[1],o.pt).over;}
      else{const kk=f[1]==='player_rush_yds'?'RBrush':f[1]==='player_reception_yds'?'RBrec':null;
        if(!kk){rec.p.base=PM.sideProbs({mean:mu,sd:1,shape:{pos:'RB',low}},f[1],o.pt).over;}else for(const z of ZS)rec.p[String(z)]=V[kk+'|'+z].sideProbs({mean:mu,sd:1,shape:{pos:'RB',low}},f[1],o.pt).over;
        rec.rbk=kk;}
      rec.default=P==='WR'&&f[1]!=='player_rush_yds'?'1.07|1':(rec.rbk?'1':'base');}
    if(!rec.default)rec.default='base';
    out.push(rec);}}
fs.writeFileSync(__dirname+'/tune_rows.json',JSON.stringify(out));console.log('rows',out.length,'depth-chart fallback rows',fb);
