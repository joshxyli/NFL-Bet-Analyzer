const fs=require('fs');const PM=require(__dirname+'/pm_new.js');const I=JSON.parse(fs.readFileSync(__dirname+'/bt_docs.json','utf8'));const res=new Map(Object.entries(I.results));
const E=I.periods.A_w10_12;const km=new Map(E.map(e=>[e.doc.eventId,e.key]));const bt=PM.backtest(E.map(e=>e.doc),res,{keyOf:d=>km.get(d.eventId),abbr:n=>n,w:0.3,gw:0.3,be:0});
console.log(JSON.stringify(bt.bet.props.map(b=>[b.label,b.bets,b.w,+b.profit.toFixed(2)])));
