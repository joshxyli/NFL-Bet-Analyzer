const fs=require('fs');const PM=require(__dirname+'/pm_new.js');const inp=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const res=new Map(Object.entries(inp.results));const km=new Map(inp.logs.map(l=>[l.doc.eventId,l.key]));const out={};
for(const w of [0.1,0.3,0.6,1.0]){const bt=PM.backtest(inp.logs.map(l=>l.doc),res,{keyOf:d=>km.get(d.eventId),abbr:n=>n,w,gw:0.3,be:0});
 out[w]=bt.bet.props.slice(0,2).map(b=>({label:b.label,bets:b.bets,w:b.w,profit:+b.profit.toFixed(3)}));}
console.log(JSON.stringify(out));
