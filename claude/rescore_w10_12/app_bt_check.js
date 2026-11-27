// overlay each configuration's chances onto the saved lines and run the published app's own PM.backtest
const fs=require('fs');const PM=require(__dirname+'/pm_new.js');const I=JSON.parse(fs.readFileSync(__dirname+'/tune_in.json','utf8'));const res=new Map(Object.entries(I.results));
const DUMP=JSON.parse(fs.readFileSync(__dirname+'/proj_dump.json','utf8'));
for(const [name,m] of Object.entries(DUMP)){const line=[];
  for(const [lab,ws] of [['wk5-11',[5,6,7,8,9,10,11]],['wk12',[12]]]){const S=I.logs.filter(e=>ws.includes(e.wk));const km=new Map(S.map(e=>[e.doc.eventId,e.key]));
    const docs=S.map(({doc})=>({...doc,o:doc.o.map((s,oi)=>{const k=doc.eventId+'|'+oi;if(!(k in m))return s;const f=s.split('|');f[6]=m[k].toFixed(4);return f.join('|');})}));
    for(const w of [0.1,0.2,0.3,0.6,1.0]){const b=PM.backtest(docs,res,{keyOf:d=>km.get(d.eventId),abbr:n=>n,w,gw:0.3,be:0}).bet.props[1];line.push(`${lab} ${w*100}%: ${b.bets} bets ${b.profit>=0?'+':''}${b.profit.toFixed(1)}u (${b.bets?(100*b.profit/b.bets).toFixed(1):0}%)`);}}
  console.log('##',name);console.log('   '+line.slice(0,5).join(' | '));console.log('   '+line.slice(5).join(' | '));}
