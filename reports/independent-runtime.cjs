const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = process.argv[2] || '/mnt/data/travel-build';
const html = readFileSync(path.join(root,'index.html'), 'utf8');
const [,literal] = html.match(/<script type="application\/json" id="dataset">(.+?)<\/script>/s);
const [,app] = html.match(/<script>(.+?)<\/script><\/body>/s);
const bundle = JSON.parse(literal);
const cities = bundle.cities;
const keys=['baku','tbilisi','budapest','vienna','prague'];
assert.deepEqual(cities.map(c=>c.id),keys);
assert(html.includes("connect-src 'none'"));
assert(!/<(?:script|img|link)\b[^>]*(?:src|href)="https?:/i.test(html.slice(0,html.indexOf('<script type="application/json"'))));
assert(!/\b(?:fetch|XMLHttpRequest|WebSocket|sendBeacon)\s*\(/.test(app));
assert(!/url\(\s*["']?https?:/i.test(html.match(/<style>(.*?)<\/style>/s)[1]));

function fresh(stored={}, useStorage=true) {
  const handlers={};
  const nodes=new Map();
  function get(id){
    if(!nodes.has(id))nodes.set(id,{
      id, innerHTML:'', textContent: id==='dataset'?literal:'', value:'',
      querySelector: selector=>get(selector),
      focus(){}, scrollIntoView(){}
    });
    return nodes.get(id);
  }
  const scope=vm.createContext({
    document:{querySelector:sel=>get(sel.slice(1)),getElementById:get,addEventListener:(n,f)=>handlers[n]=f},
    localStorage:{getItem:key=>{if(!useStorage)throw Error('denied');return stored[key]||null},
      setItem:(key,val)=>{if(!useStorage)throw Error('denied');stored[key]=val}},
    window:{addEventListener(){},print(){}}
  });
  vm.runInContext(app,scope);
  return {scope,get,stored,handlers,eval:code=>vm.runInContext(code,scope),
    click:(dataset={})=>handlers.click({target:{closest:()=>({dataset,hasAttribute:()=>false})}})};
}
function straightMeters(a,b){
  const rad=x=>x*Math.PI/180;
  const [aLat,aLon]=a.map(rad);
  const [bLat,bLon]=b.map(rad);
  const chord=Math.sin((bLat-aLat)/2)**2+Math.cos(aLat)*Math.cos(bLat)*Math.sin((bLon-aLon)/2)**2;
  return 12742000*Math.asin(Math.sqrt(chord));
}
let largestEndpointSnap=0;
const cached={};
const b=fresh(cached);
const metrics=[];
for(let i=0;i<cities.length;i++){
  const city=cities[i];
  b.click({city:city.id});
  assert.match(b.get('city').innerHTML,new RegExp('>'+city.city+'</h2>'));
  assert.equal((b.get('city').innerHTML.match(/class="day"/g)||[]).length,city.days.length);
  assert.equal((b.get('city').innerHTML.match(/class="stay"/g)||[]).length,city.stays.length);
  assert(city.stays.every(s=>new URL(s.url).hostname.endsWith('airbnb.com')));
  const originalTotal=b.eval('total(current)');
  const originalFood=b.eval('budget(current).food');
  b.handlers.input({target:{dataset:{cost:'food'},value:String(originalFood+101)}});
  assert.equal(b.eval('total(current)'),originalTotal+303);
  b.handlers.input({target:{dataset:{cost:'car'},value:'300'}});
  assert.equal(b.eval('total(current)'),originalTotal+603);
  b.click({stay:'1'});
  assert.equal(b.eval('budget(current).stay'),city.stays[1].price);
  for(const [index,photo] of bundle.photos[city.id].entries()){
    assert(photo.data.startsWith('data:image/webp;base64,'));
    const embedded=Buffer.from(photo.data.split(',')[1],'base64');
    const source=readFileSync(path.join(root,'assets',photo.file));
    assert(embedded.equals(source));
    assert.equal(embedded.toString('utf8',0,4),'RIFF');
    assert.equal(embedded.toString('utf8',8,12),'WEBP');
    assert(photo.author && photo.license && new URL(photo.licenseUrl).protocol==='https:');
    assert(photo.checked && photo.caption);
    assert(b.get('gallery').innerHTML.includes(photo.author));
    assert(b.get('gallery').innerHTML.includes(photo.licenseUrl));
    b.click({gallery:'1'});
  }
  const map=bundle.maps[city.id];
  const routes=map.anchors.flatMap(a=>a.routes);
  for(const anchor of map.anchors){
    b.handlers.change({target:{id:'anchor-select',value:anchor.id}});
    for(const route of anchor.routes){
      if(route.path.length<2){assert(!Number.isFinite(route.min)||route.estimated); continue;}
      assert(route.estimated || /OSM|Valhalla|FOSSGIS/.test(route.status+' '+route.routeSource));
      const snap=Math.max(straightMeters(anchor.start,route.path[0]),straightMeters(route.point,route.path.at(-1)));
      largestEndpointSnap=Math.max(largestEndpointSnap,snap);
      assert(snap<125,route.name+' endpoints must be within 125 m of the mapped points');
      assert(route.meters>=straightMeters(anchor.start,route.point)-125);
      assert(Math.abs(route.km-route.meters/1000)<0.03);
      assert(Math.abs(route.min-route.seconds/60)<1.01);
    }
    const toggles=b.get('map').innerHTML.match(/data-route="/g)||[];
    assert.equal(toggles.length,anchor.routes.length);
    if(anchor.routes.length>1){
      b.click({route:'1'});
      assert.match(b.get('map').innerHTML,/data-route="1" aria-pressed="true"/);
    }
  }
  metrics.push({city:city.id,nights:city.nights,days:city.days.length,stays:city.stays.length,photos:bundle.photos[city.id].length,anchors:map.anchors.length,routes:routes.length,tracedPaths:routes.filter(x=>x.path.length>1).length,timedRoutes:routes.filter(x=>Number.isFinite(x.min)).length});
}
b.handlers.change({target:{id:'left-city',value:'vienna'}});
assert.match(b.get('compare').innerHTML,/<th scope="col">Vienna<\/th>/);
const restored=fresh(cached);
assert.equal(restored.eval('current.id'),'prague');
assert.equal(restored.eval('budget(current).car'),300);
assert.equal(restored.eval('state.left'),'vienna');
const freshNoStorage=fresh({},false);
assert.equal(freshNoStorage.eval('current.id'),'baku');
freshNoStorage.click({city:'prague'});
assert.equal(freshNoStorage.eval('current.id'),'prague');
console.log(JSON.stringify({mode:'Node VM with simulated document and localStorage, using final embedded scripts and data.',networkAccess:'Absent by construction. Connect-src none present.',metrics,largestEndpointSnapMeters:Math.round(largestEndpointSnap),localState:true,storageDeniedFallback:true,comparison:true,sourceSha256:require('node:crypto').createHash('sha256').update(html).digest('hex'),sizeBytes:Buffer.byteLength(html) },null,2));
