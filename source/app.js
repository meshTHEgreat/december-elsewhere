'use strict';
const book = JSON.parse(document.querySelector('#dataset').textContent);
const cities = book.cities;
const byId = Object.fromEntries(cities.map(city => [city.id, city]));
const el = id => document.getElementById(id);
const h = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const money = value => 'SAR ' + Math.round(value).toLocaleString('en-US');
const external = (url, label, cls='') => /^https:\/\//.test(url || '') ? '<a class="'+h(cls)+'" href="'+h(url)+'" target="_blank" rel="noopener noreferrer">'+h(label)+'</a>' : '';
const string = x => typeof x==='object' && x!==null ? Object.values(x).map(string).join(' · ') : String(x??'');
function read() { try { return JSON.parse(localStorage.getItem('december-elsewhere-v1')) || {}; } catch { return {}; } }
let state = read();
function persist() { try { localStorage.setItem('december-elsewhere-v1', JSON.stringify(state)); } catch {} }
let current = byId[state.city] || cities[0];
let routeIndex=0, anchorId='', slide=0;
const opening = [
 'Nonstop schedule',
 'Old Town and day trips',
 'Markets and baths',
 'Museums and markets',
 'Five nights by tram'
];
const fieldLabels={flight:'Base airfare',bags:'Baggage & seat fees',stay:'Accommodation with fees',food:'Meals & drinks',transit:'Airport & local transport',activities:'Admissions & activities',daytrip:'Driver, tours or rail excursions',insurance:'Entry fees & insurance',car:'Rental base',fuel:'Fuel',parking:'Parking',cover:'Rental insurance',tolls:'Road tolls',contingency:'Contingency'};
const groupFields = new Set(['stay','daytrip','car','fuel','parking','cover','tolls']);
const budgetKeys = Object.keys(fieldLabels);
const carFields = new Set(['car','fuel','parking','cover','tolls']);
const n = x => Math.max(0, Math.min(150000, Number(x) || 0));
function budget(city){ const vals={...city.budget,...state.budgets?.[city.id]}; return Object.fromEntries(budgetKeys.map(key=>[key,n(vals[key])])); }
function total(city){return Object.entries(budget(city)).reduce((sum,[key,value])=>sum+value*(groupFields.has(key)?1:3),0);}
function img(city,index=0) { const images=book.photos[city.id]||[]; return images[index]||images[0]; }
function backdrop(photo){return (photo?'<img class="backdrop" src="'+photo.data+'" alt="" width="'+(photo.width||1440)+'" height="'+(photo.height||960)+'">':'')+'<div class="shade"></div>';}
function paintHero(){
 const photo=img(cities[0]);
 el('top').innerHTML=backdrop(photo)+'<div class="wrap hero-inner"><h1>December,<br><em>elsewhere.</em></h1><p class="hero-blurb">5–12 Dec 2026 · Medina · 3 adults</p></div>'+(photo?'<span class="hero-credit">'+h(photo.caption||'Baku')+' · '+h(photo.author||'')+'</span>':'');
}
function clock(city){return string(city.dates);}
function paintPick(){
 el('destinations').innerHTML='<div class="pick-head"><h2>Choose a city</h2><p class="small">Estimated trip cost per adult</p></div><div class="city-list">'+cities.map((city,i)=>'<button class="city-tab" data-city="'+city.id+'" aria-pressed="'+(city===current)+'"><span><strong class="city-name">'+h(city.city)+'</strong><small class="city-detail">'+h(clock(city))+' · '+h(opening[i])+'</small></span><span class="city-price" id="pick-price-'+city.id+'">'+h(money(total(city)/3))+'</span></button>').join('')+'</div>';
}
const hBed = value => typeof value==='number'?value+' beds':string(value);
function stayCard(stay,i){const selected=(state.stays?.[current.id]??0)===i; return '<section class="stay"><span class="meta">'+h(stay.platform||'Airbnb')+'</span><h3>'+h(stay.name)+'</h3><p class="price">'+(stay.price?money(stay.price):'Price to check')+'</p><p class="small">'+h(stay.status||'Earlier Airbnb observation · 23 Nov 2026')+'</p><div class="stay-spec">'+[stay.bedrooms!=null?stay.bedrooms+' bedrooms':null,stay.beds?hBed(stay.beds):null,typeof stay.bathrooms==='number'?stay.bathrooms+' bath':stay.bathrooms||'Bathrooms: check listing',stay.rating?stay.rating+'/5'+(stay.reviews?' · '+stay.reviews+' reviews':''):null].filter(Boolean).map(x=>'<span class="pill">'+h(x)+'</span>').join('')+'</div><p><strong>'+h(stay.area||'Location from listing')+'</strong> · '+h(stay.notes||'Check sleeping layout and arrival arrangements with the listing host.')+ '</p>'+ (stay.access?'<p class="small">'+h(stay.access)+'</p>':'')+'<p class="small photo-note">Photos and availability are on the listing.</p><div class="stay-cta">'+external(stay.url,'Listing & photos','action')+'<button class="action" data-stay="'+i+'" aria-pressed="'+selected+'">'+(selected?'In your budget':'Use in budget')+'</button></div></section>';}
function section(id,title,body){return '<section id="'+id+'" class="section wrap"><h2>'+h(title)+'</h2>'+body+'</section>';}
function paintGallery(){const images=book.photos[current.id]||[];const p=images[slide];el('gallery').innerHTML=p?'<figure class="visual"><img src="'+p.data+'" alt="'+h(p.title||current.city)+'" loading="lazy" decoding="async"><figcaption class="small">'+h(p.caption||p.title||current.city)+' · '+h(p.author||'')+' · '+external(p.url,'Photo source')+' · '+external(p.licenseUrl,p.license||'License')+(p.modifications?' · '+h(p.modifications):'')+'</figcaption></figure>'+(images.length>1?'<div class="gallery-tools"><button class="action" data-gallery="-1">Previous photo</button><span class="small">'+(slide+1)+' / '+images.length+'</span><button class="action" data-gallery="1">Next photo</button></div>':''):'';}
function budgetField(city,key){
 return '<label for="cost-'+key+'"><span>'+h(fieldLabels[key])+' <small class="muted">· '+(groupFields.has(key)?'group':'each')+'</small></span><input id="cost-'+key+'" type="number" min="0" max="150000" step="1" inputmode="numeric" data-cost="'+key+'" value="'+budget(city)[key]+'"></label>';
}
function paintCity(){
 const city=current, photo=img(city,city.id==='baku'?1:0), f=city.flights||{}, transport=city.transport||{};
 el('city').innerHTML='<div class="chapter" id="chapter">'+backdrop(photo)+'<div class="wrap chapter-inner"><p class="meta">'+h(city.country)+' · '+h(clock(city))+'</p><h2 tabindex="-1">'+h(city.city)+'</h2></div>'+(photo?'<span class="chapter-credit">'+h(photo.caption||city.city)+' · '+h(photo.author||'')+'</span>':'')+'</div><nav class="wrap city-subnav" aria-label="Destination sections"><a href="#flight">Flights</a><a href="#stays">Stays</a><a href="#walk">Walks</a><a href="#itinerary">Itinerary</a><a href="#budget">Budget</a><a href="#photos">Photos</a></nav>'
 +section('flight','Flights','<div class="split"><div><p class="small">'+h(f.status||'Published schedules; checkout not verified')+'</p><div class="flight-leg"><b>Outbound</b><br>'+h(string(f.out))+'</div><div class="flight-leg"><b>Return</b><br>'+h(string(f.back))+'</div><details class="flight-details"><summary>Baggage and booking notes</summary><p class="small">'+h(f.bags||'Baggage depends on fare family; price at checkout.')+'</p><p>'+h(f.note)+'</p><p class="small">'+(f.links||[]).map(l=>external(l.url,l.label)).join(' · ')+'</p></details></div><div><div class="rule"><h3>Entry requirements</h3><p>'+h(city.entry)+'</p></div><div class="rule"><h3>Winter & daylight</h3><p>'+h(city.winter)+' '+h(city.light)+'</p></div></div></div>')
 +section('stays','Stays','<p class="section-lead">Prices shown for three adults. Recheck the beds, total price and check-in before booking.</p><div class="stays">'+city.stays.map(stayCard).join('')+'</div>'+ (city.alternatives?.length?'<details class="rule"><summary>Other stays</summary><p>'+city.alternatives.map(a=>external(a.url,a.name||a.label)+' · '+h([a.notes||a.note,a.status].filter(Boolean).join(' · ')||'Check dates, beds and total')).join('<br>')+'</p></details>':''))
 +section('walk','Walks and transport','<div id="map"></div>'+ (transport.city?'<div class="transport-notes"><h3>Getting around</h3><dl>'+[['In the city',transport.city],['Airport transfer',transport.transfer],['Day trips',transport.day],['Short car hire',transport.rental]].filter(([,v])=>v).map(([k,v])=>'<div><dt>'+h(k)+'</dt><dd>'+h(v)+'</dd></div>').join('')+'</dl></div>':''))
 +section('itinerary','Itinerary','<p class="section-lead">Times and daily costs are estimates. Check opening hours before you go.</p><div class="daylist">'+city.days.map((d,i)=>'<details class="day" '+(i===0?'open':'')+'><summary><span>'+h(Number(d.date.slice(8))+' Dec')+'</span><strong>'+h(d.title)+'</strong></summary><div class="day-body"><ol class="stops">'+(d.stops||[]).map(s=>'<li><strong>'+h(s.time)+' · '+h(s.name)+'</strong><br><span class="small">'+h([s.duration,s.mode,s.travel].filter(Boolean).join(' · '))+'</span> '+h(s.note)+'</li>').join('')+'</ol><p><b>Meals</b> · '+h(d.meal)+' <strong>'+money(d.cost)+' per adult</strong> for the day.</p><p class="small"><b>Alternative</b> · '+h(d.backup)+'</p></div></details>').join('')+'</div>')
 +section('budget','Budget','<p class="section-lead">Costs for the full trip, in SAR.</p><div class="budget-layout"><aside class="budget-total" id="total" aria-live="polite"></aside><div><div class="budget-fields">'+budgetKeys.filter(key=>!carFields.has(key)).map(key=>budgetField(city,key)).join('')+'</div><details class="car-costs" '+(budgetKeys.some(key=>carFields.has(key)&&budget(city)[key])?'open':'')+'><summary>Car rental costs</summary><div class="budget-fields">'+budgetKeys.filter(key=>carFields.has(key)).map(key=>budgetField(city,key)).join('')+'</div></details></div></div><div class="budget-actions"><button class="action" data-reset>Reset city budget</button> <button class="action" data-print>Print itinerary</button></div>')
 +section('photos','Photos','<div id="gallery"></div>');
 paintGallery();paintMap();paintTotal();
}
function paintMap(){
 const map=book.maps[current.id], node=el('map');
 if(!map?.anchors?.length){node.textContent='Offline routing could not be verified for this destination.';return;}
 const selected=current.stays[state.stays?.[current.id]??0];
 const anchor=map.anchors.find(a=>a.id===anchorId)||map.anchors.find(a=>a.stays?.includes(String(selected?.id)))||map.anchors[0];
 const routes=anchor.routes||[];
 const route=routes[routeIndex]||routes[0];
 const points=[anchor.start,...routes.flatMap(r=>[r.point,...(r.path||[])])].filter(p=>Array.isArray(p)&&p.length===2);
 const lat=points.map(p=>p[0]), lon=points.map(p=>p[1]);
 const sx=(Math.max(...lon)-Math.min(...lon))*Math.cos(anchor.start[0]*Math.PI/180), sy=Math.max(...lat)-Math.min(...lat), scale=Math.min(495/Math.max(sx,.0006),270/Math.max(sy,.0006));
 const cx=(Math.max(...lon)+Math.min(...lon))/2,cy=(Math.max(...lat)+Math.min(...lat))/2;
 const xy=p=>[300+(p[1]-cx)*Math.cos(anchor.start[0]*Math.PI/180)*scale,171-(p[0]-cy)*scale];
 const dot=(p,fill,size)=>{const [x,y]=xy(p);return '<circle cx="'+x+'" cy="'+y+'" r="'+size+'" fill="'+fill+'" stroke="#fff" stroke-width="2"/>';};
 const poly=(r,selected)=>r.path?.length>1?'<polyline points="'+r.path.map(p=>xy(p).map(x=>x.toFixed(1)).join(',')).join(' ')+'" fill="none" stroke="'+(selected?'#7c3822':'#9eab89')+'" stroke-width="'+(selected?'4':'2')+'" stroke-linecap="round" stroke-linejoin="round"/>':'';
 const connector=(r)=>{const [x,y]=xy(anchor.start),[dx,dy]=xy(r.point);return '<line x1="'+x+'" y1="'+y+'" x2="'+dx+'" y2="'+dy+'" stroke="#7c3822" stroke-dasharray="5 5" stroke-width="2"/>';};
 const matches=map.anchors.some(a=>a.stays?.includes(String(selected?.id)));
 const caveat=matches?'Walks start from a public landmark.':'No public starting point was confirmed for this stay.';
 const anchorPicker='<div class="anchor-picker"><label for="anchor-select">Walking from</label><select id="anchor-select">'+map.anchors.map(a=>'<option value="'+h(a.id)+'" '+(a===anchor?'selected':'')+'>'+h(a.name)+'</option>').join('')+'</select><p class="small">'+h(caveat)+' '+h(anchor.note||'')+'</p></div>';
 const routeDetails='<div id="route-note" class="small" aria-live="polite">'+(route?'<strong>'+h(route.name)+'</strong> · '+external(route.url,'Directions online'):'No route calculated')+'</div>';
 node.innerHTML=anchorPicker+'<div class="route-layout"><div><div class="mapbox"><svg viewBox="0 0 600 350" role="img" aria-label="'+h('Pedestrian paths from '+anchor.name)+'"><defs><pattern id="grid" width="27" height="27" patternUnits="userSpaceOnUse"><path d="M27 0H0V27" stroke="#c8cfb7" fill="none" opacity=".55"/></pattern></defs><rect width="600" height="350" fill="url(#grid)"/><text x="553" y="29" class="map-label">N ↑</text>'+routes.filter(r=>r!==route).map(r=>poly(r,false)).join('')+(route?(poly(route,true)||connector(route)):'')+routes.map(r=>dot(r.point,r===route?'#7c3822':'#5a6a44',r===route?7:4)).join('')+dot(anchor.start,'#194637',8)+'</svg></div><p class="small">'+h(map.attribution||'© OpenStreetMap contributors')+' Walking times are estimates.</p></div><div>'+routeDetails+routes.map((r,i)=>'<button class="route-toggle" data-route="'+i+'" aria-pressed="'+(r===route)+'"><strong>'+h(r.name)+'</strong><small>'+(r.min==null?'Walk time unavailable':(r.estimated?'~':'')+h(r.min)+' min · '+(r.estimated?'~':'')+h(r.km)+' km'+(r.estimated?' · estimate':''))+'</small></button>').join('')+'</div></div>';
}
function paintTotal(){const sum=total(current);el('total').innerHTML='<span class="meta">Group total</span><strong id="total-group">'+money(sum)+'</strong><span id="total-person">'+money(sum/3)+' per adult</span><p class="small">'+(sum/3>6000?'Above the preferred budget.':sum/3<4000?'Below the target range.':'Within the preferred range.')+' Includes contingency.</p>';}
function compareOptions(selected){return cities.map(c=>'<option value="'+c.id+'" '+(c.id===selected?'selected':'')+'>'+h(c.city)+'</option>').join('');}
const comparePrices = {
 person: ['Per adult',c=>money(total(c)/3)],
 group: ['For three',c=>money(total(c))],
 stay: ['Stay',c=>money(budget(c).stay)],
 food: ['Meals per adult',c=>money(budget(c).food)],
 transit: ['Local transport per adult',c=>money(budget(c).transit)]
};
function refreshPrices(){
 el('pick-price-'+current.id).textContent=money(total(current)/3);
 [byId[state.left]||cities[0],byId[state.right]||cities[1]].forEach((city,i)=>{
  if(city===current) for(const [key,[,price]] of Object.entries(comparePrices)) el('compare-'+i+'-'+key).textContent=price(city);
 });
}
function paintCompare(){
 const A=byId[state.left]||cities[0], B=byId[state.right]||cities[1];
 const prices=Object.entries(comparePrices).map(([key,[label,price]])=>[label,price,key]);
 const items=[...prices.slice(0,2),['Dates',clock],['Nights',c=>c.nights],...prices.slice(2)];
 const details=[['Outbound',c=>string(c.flights?.out)],['Return',c=>string(c.flights?.back)],['Entry',c=>c.entry],['Winter',c=>c.winter]];
 const rows=list=>list.map(([label,get,key])=>'<tr><th scope="row">'+h(label)+'</th>'+[A,B].map((city,i)=>'<td'+(key?' id="compare-'+i+'-'+key+'"':'')+'>'+h(get(city))+'</td>').join('')+'</tr>').join('');
 const head='<thead><tr><th scope="col">Trip detail</th><th scope="col">'+h(A.city)+'</th><th scope="col">'+h(B.city)+'</th></tr></thead>';
 const container=el('compare'), expanded=container.querySelector('.compare-details')?.open;
 container.innerHTML='<h2>Compare cities</h2><div class="compare-controls"><label for="left-city">First city<select id="left-city">'+compareOptions(A.id)+'</select></label><label for="right-city">Second city<select id="right-city">'+compareOptions(B.id)+'</select></label></div><div class="compare-scroll"><table>'+head+'<tbody>'+rows(items)+'</tbody></table></div><details class="compare-details" '+(expanded?'open':'')+'><summary>Flights, entry and winter weather</summary><div class="compare-scroll"><table>'+head+'<tbody>'+rows(details)+'</tbody></table></div></details>';
}
function paintEvidence(){el('evidence').innerHTML='<h2>Sources</h2><p class="section-lead">Stay prices were observed on 23 November 2026. Flight times follow published schedules. Confirm both before booking.</p>'+cities.map(c=>'<details><summary>'+h(c.city)+' sources</summary><p class="small">Earlier estimate for three: '+h(c.priorTotal)+'.</p><ul>'+[...(c.sources||[]),...(book.photos[c.id]||[]).map(p=>({label:(p.title||'Destination image')+' · '+(p.author||''),url:p.url,status:p.license,checked:p.checked||'2026-11-23'}))].map(s=>'<li>'+external(s.url,s.label||s.name||s.url)+' <span class="small">'+h([s.status,s.checked,s.note].filter(Boolean).join(' · '))+'</span></li>').join('')+'</ul></details>').join('')+'<details><summary>Routes & currency reference</summary><p class="small">Retrieved pedestrian paths and separately labeled walking estimates are packaged offline. Estimated directions use straight-line distance × 1.37 and an assumed 3.6 km/h. Actual crossings, grades and weather may change the time. '+external('https://www.openstreetmap.org/copyright','OpenStreetMap attribution')+' · '+external('https://valhalla.github.io/valhalla/','Valhalla routing')+'. The calculator sums SAR inputs directly; prior examples were rounded during the 23 November 2026 research. '+external('https://www.sama.gov.sa/en-us/currency/finexc/pages/currency.aspx','Saudi Central Bank FX reference')+' provides the exchange-rate archive. No live FX conversion.</p></details>';}
document.addEventListener('click',e=>{
 const b=e.target.closest('button');if(!b)return;
 if(b.dataset.city){current=byId[b.dataset.city];state.city=current.id;anchorId='';routeIndex=0;slide=0;persist();paintPick();paintCity();el('chapter').querySelector('h2').focus({preventScroll:true});el('chapter').scrollIntoView({block:'start'});}
 if(b.dataset.route!==undefined){routeIndex=Number(b.dataset.route);paintMap();el('map').querySelector('[aria-pressed=true]')?.focus({preventScroll:true});}
 if(b.dataset.gallery){const length=book.photos[current.id]?.length||1;slide=(slide+Number(b.dataset.gallery)+length)%length;paintGallery();el('gallery').querySelector('[data-gallery="'+b.dataset.gallery+'"]')?.focus({preventScroll:true});}
 if(b.dataset.stay!==undefined){const i=Number(b.dataset.stay), stay=current.stays[i];state.stays={...state.stays,[current.id]:i};state.budgets={...state.budgets,[current.id]:{...state.budgets?.[current.id],stay:stay.price||budget(current).stay}};persist();el('stays').querySelector('.stays').innerHTML=current.stays.map(stayCard).join('');el('stays').querySelector('[data-stay="'+i+'"]')?.focus({preventScroll:true});el('cost-stay').value=budget(current).stay;anchorId='';routeIndex=0;paintMap();paintTotal();refreshPrices();}
 if(b.hasAttribute('data-reset')){if(state.budgets)delete state.budgets[current.id];if(state.stays)delete state.stays[current.id];anchorId='';routeIndex=0;persist();paintCity();el('budget').querySelector('[data-reset]').focus({preventScroll:true});refreshPrices();}
 if(b.hasAttribute('data-print'))window.print();
});
document.addEventListener('input',e=>{const key=e.target.dataset.cost;if(!key)return;state.budgets={...state.budgets,[current.id]:{...state.budgets?.[current.id],[key]:n(e.target.value)}};persist();paintTotal();refreshPrices();});
document.addEventListener('change',e=>{if(e.target.dataset?.cost)e.target.value=budget(current)[e.target.dataset.cost];if(e.target.id==='anchor-select'){anchorId=e.target.value;routeIndex=0;paintMap();el('anchor-select').focus({preventScroll:true});}if(e.target.id==='left-city'||e.target.id==='right-city'){state[e.target.id.split('-')[0]]=e.target.value;persist();paintCompare();el(e.target.id)?.focus({preventScroll:true});}});
let printedDays=[];
window.addEventListener('beforeprint',()=>{printedDays=[...document.querySelectorAll('.day:not([open])')];printedDays.forEach(d=>d.open=true);});
window.addEventListener('afterprint',()=>{printedDays.forEach(d=>d.open=false);printedDays=[];});
paintHero();paintPick();paintCity();paintCompare();paintEvidence();
