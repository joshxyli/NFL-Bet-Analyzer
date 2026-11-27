// usage: node eval.js <old.html> <new.html> <jobs.json> <out.json>
const fs=require('fs'),path=require('path'),os=require('os');
function loadPM(file,tag){const h=fs.readFileSync(file,'utf8');const i=h.indexOf('const PM = (() => {'),j=h.indexOf('})();',i)+5;
  const p=path.resolve(__dirname,'pm_'+tag+'.js');fs.writeFileSync(p,h.slice(i,j)+'\nmodule.exports = PM;');return require(p);}
const OLD=loadPM(process.argv[2],'old'),NEW=loadPM(process.argv[3],'new');
const jobs=JSON.parse(fs.readFileSync(process.argv[4],'utf8'));
const thinOld=(mk,pt,mean)=>OLD.MARKETS[mk].unit==='yds'&&(pt<5||mean<15);
const out=jobs.map(r=>{
  const base={mean:r.mean,sd:r.sd};
  const po=thinOld(r.mk,r.pt,r.mean)?OLD.empirical({g:r.g},r.mk,r.pt):OLD.sideProbs(base,r.mk,r.pt);
  const res={old:po.over,oldThin:thinOld(r.mk,r.pt,r.mean)};
  for(const low of [0,1]){const pj=r.pos?{...base,shape:{pos:r.pos,low}}:base;
    const pn=NEW.isThin(pj,r.mk,r.pt)?NEW.empirical({g:r.g},r.mk,r.pt):NEW.sideProbs(pj,r.mk,r.pt); res['new'+low]=pn.over;}
  return res;});
fs.writeFileSync(process.argv[5],JSON.stringify(out));
