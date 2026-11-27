// node variants.js jobs.json out.json : over-chance for each shape row under model variants (low = 0 and 1)
const fs=require('fs');const src=fs.readFileSync(__dirname+'/pm_new.js','utf8');
const mk=(tag,f)=>{const p=__dirname+'/pm_v_'+tag+'.js';fs.writeFileSync(p,f(src));return require(p);};
const half=s=>s.replace('z: [-2.164, -0.149, 2.253]','z: [-2.164, -0.149, 1.1265]').replace('z: [-1.219, -0.191, 1.545]','z: [-1.219, -0.191, 0.7725]').replace('z: [-2.219, -0.025, 2.381]','z: [-2.219, -0.025, 1.1905]');
const rbrec=s=>s.replace('z: [-1.219, -0.191, 1.545]','z: [-1.219, -0.191, 0.7725]');const wr25=s=>rbrec(s).replace('z: [-2.164, -0.149, 2.253]','z: [-2.164, -0.149, 1.68975]');
const V={cur:mk('cur',s=>s),halfZ:mk('halfz',half),rbRecHalf:mk('rbrec',rbrec),rbRecHalf_wr25:mk('wr25',wr25)};
if(V.halfZ.sideProbs({mean:30,sd:18,shape:{pos:'WR',low:1}},'player_reception_yds',20.5).under===V.cur.sideProbs({mean:30,sd:18,shape:{pos:'WR',low:1}},'player_reception_yds',20.5).under) throw 'variant not applied';
const J=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
fs.writeFileSync(process.argv[3],JSON.stringify(J.map(r=>{const o={};if(!r.pos)return o;for(const [k,P] of Object.entries(V))for(const low of[0,1])o[k+low]=P.sideProbs({mean:r.mean,sd:r.sd,shape:{pos:r.pos,low}},r.mk,r.pt).over;return o;})));
