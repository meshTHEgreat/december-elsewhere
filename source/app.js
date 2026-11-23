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
const pageLocation = () => (window.location?.hash || '').slice(1).split('/');
let current = byId[pageLocation()[0]] || byId[state.city] || cities[0];
let routeIndex = 0, anchorId = '', slide = 0;
let chapterObserver;
let walkListExpanded = false;
const compactWalks = window.matchMedia?.('(max-width: 42rem)');
const shortLandscapeWalks = window.matchMedia?.('(max-width: 54rem) and (orientation: landscape) and (max-height: 31rem)');
let lastPhotoTrigger;
const fieldLabels={flight:'Base airfare',bags:'Baggage & seat fees',stay:'Accommodation with fees',food:'Meals & drinks',transit:'Airport & local transport',activities:'Admissions & activities',daytrip:'Driver, tours or rail excursions',insurance:'Entry fees & insurance',car:'Rental base',fuel:'Fuel',parking:'Parking',cover:'Rental insurance',tolls:'Road tolls',contingency:'Contingency'};
const groupFields = new Set(['stay','daytrip','car','fuel','parking','cover','tolls']);
const budgetKeys = Object.keys(fieldLabels);
const carFields = new Set(['car','fuel','parking','cover','tolls']);
const n = x => Math.max(0, Math.min(150000, Number(x) || 0));
function budget(city){ const vals={...city.budget,...state.budgets?.[city.id]}; return Object.fromEntries(budgetKeys.map(key=>[key,n(vals[key])])); }
function total(city){return Object.entries(budget(city)).reduce((sum,[key,value])=>sum+value*(groupFields.has(key)?1:3),0);}
function photograph(city, file) {
 const images = book.photos[city.id];
 return images.find(image => image.file === file) || images[0];
}
function imageMarkup(photo, cls = '', alt = photo.title, lazy = true) {
 return '<img class="' + cls + '" src="' + photo.data + '" alt="' + h(alt) + '" width="' + photo.width
  + '" height="' + photo.height + '" decoding="async"' + (lazy ? ' loading="lazy"' : '') + '>';
}
function photoCredit(photo, downloadable = false) {
 return h(photo.caption) + ' · ' + h(photo.author) + ' · ' + external(photo.url, 'Photo source')
  + ' · ' + external(photo.licenseUrl, photo.license) + (photo.modifications ? ' · ' + h(photo.modifications) : '')
  + (downloadable ? '<a class="photo-download" href="'+h(photo.data)+'" download="'+h(photo.file)+'">Download photo ↓</a>' : '');
}
function clock(city) { return string(city.dates); }
function paintPick() {
 el('city-index').innerHTML = '<div class="city-list">' + cities.map(city => '<button class="city-tab" data-city="'+city.id
  +'" aria-pressed="'+(city === current)+'"><span><strong class="city-name">'+h(city.city)+'</strong><small class="city-detail">'
  +h(clock(city))+' · '+h(book.editorial.cities[city.id].tag)+'</small></span><span class="city-price" id="pick-price-'+city.id+'">'
  +h(money(total(city)/3))+'</span><span class="city-arrow" aria-hidden="true">↗</span></button>').join('') + '</div>';
}
const hBed = value => typeof value === 'number' ? value + ' beds' : string(value);
const stayDecisionNotes = {
 '24291154': 'Two beds for three adults. Confirm the airport transfer and late check-in.',
 '1411583738365530757': 'Confirm bedding and late access. Check wind on the 15th-floor balcony.',
 '1129688233295307149': 'Three separate beds if the singles stay separate. Check stairs and heating.',
 '1143563128668540800': 'Check private balcony access and the station walk with bags.',
 '33505706': 'Studio or one bedroom unconfirmed. Check the third bed and winter terrace access.',
 '888747837006251329': 'Allow for longer transfers. The map shows a wider district.',
 '1644751971236465063': 'Confirm beds and location. Online check-in is required.',
 '47782977': 'The park is public. Check station access. Walks start at a district hub.',
 '41492147': 'Confirm late check-in. City tax is CZK 50 per person per night, plus a processing fee.',
 '1566707663347121616': 'Confirm the stop, beds and stairs. Old Town walks are a city example.'
};
function stayCard(stay, i) {
 const selected = (state.stays?.[current.id] ?? 0) === i;
 const outdoor = stayOutdoor(stay);
 const specs = [stay.bedrooms != null ? stay.bedrooms + ' bedrooms' : null, stay.beds ? hBed(stay.beds) : null,
  typeof stay.bathrooms === 'number' ? stay.bathrooms + ' bath' : stay.bathrooms || 'Bathrooms: check listing',
  stay.rating ? stay.rating + '/5' + (stay.reviews ? ' · ' + stay.reviews + ' reviews' : '') : null];
 const caveat = stayDecisionNotes[stay.id] || 'Check the bed layout and arrival arrangements.';
 const priceNote = stay.price && stay.checked === '2026-11-23'
  ? 'For three adults · seen 23 Nov 2026 (Medina time). Check fees, cancellation and availability.'
  : stay.status || 'Check today’s price for three adults.';
 return '<section class="stay"><span class="meta">'+h(stay.platform||'Airbnb')+'</span><h3>'+h(stay.name)+'</h3><p class="price">'
  +(stay.price ? money(stay.price) : 'Check price')+'</p><p class="small stay-price-note">'+h(priceNote)
  +'</p><div class="stay-spec">'+specs.filter(Boolean).map(spec => '<span class="pill">'+h(spec)+'</span>').join('')
  +'</div><div class="outdoor-space" data-access="'+h(outdoor.kind)+'"><strong>'+h(outdoor.label)+'</strong><p class="small">'+h(caveat)
  +'</p></div><div class="stay-cta">'+external(stay.url,'Listing & photos','action')+'<button class="action" data-stay="'+i
  +'" aria-pressed="'+selected+'">'+(selected ? 'Stay selected' : 'Use this stay')+'</button></div>'
  +'<details class="stay-notes"><summary>Listing notes</summary><p><strong>'+h(stay.area||'Location from listing')+'</strong> · '+h(stay.notes)
  +'</p><p>'+h(outdoor.note)+'</p><p class="small">'+h(stay.status||'Earlier Airbnb observation · 23 Nov 2026')+'</p></details></section>';
}
function section(id, title, body) {
 return '<section id="'+id+'" class="section wrap" data-chapter-section><h2 tabindex="-1">'+h(title)+'</h2>'+body+'</section>';
}
function galleryControls(images) {
 return '<div class="gallery-tools"><button class="action" data-gallery="-1" aria-label="Previous photo"><span aria-hidden="true">←</span></button><span class="small">'
  +(slide+1)+' / '+images.length+'</span><button class="action" data-gallery="1" aria-label="Next photo"><span aria-hidden="true">→</span></button></div>';
}
function paintGallery() {
 const images = book.photos[current.id];
 const photo = images[slide];
 const figure = '<figure class="visual"><button type="button" class="photo-open" data-photo-open aria-label="View photo full screen: '+h(photo.title)+'">'
  +imageMarkup(photo)+'<span aria-hidden="true">↗</span></button><figcaption class="small">'+photoCredit(photo, true)+'</figcaption></figure>';
 el('gallery').innerHTML = figure + galleryControls(images);
 if (el('photo-dialog').open) paintPhotoDialog();
}
function paintPhotoDialog() {
 const images = book.photos[current.id];
 const photo = images[slide];
 el('photo-dialog').innerHTML = '<div class="lightbox-bar"><p>'+h(current.city)+' photos</p><button type="button" class="action" data-photo-close autofocus>Close <span aria-hidden="true">×</span></button></div>'
  +'<figure class="lightbox-figure">'+imageMarkup(photo, '', photo.title, false)+'<figcaption class="small">'+photoCredit(photo, true)+'</figcaption></figure>'
  +galleryControls(images);
}
const chapterLinks = [['intro','Arrival'],['stays','Stays'],['walk','Walks'],['winter','Winter'],['itinerary','Itinerary'],['budget','Budget'],['photos','Photos']];
function chapterNav(city) {
 const links = chapterLinks.map(([id, title]) => '<a data-jump="'+id+'" href="#'+id+'">'+title+'</a>').join('');
 return '<nav class="city-subnav" aria-label="Destination sections"><div class="wrap chapter-nav-inner">'
  +'<a class="chapter-index-link" href="#destinations"><span aria-hidden="true">↑</span> All cities</a>'
  +'<div class="chapter-jumps">'+links+'</div><details class="chapter-menu"><summary aria-label="Sections in '+h(city.city)
  +'"><span class="chapter-menu-current">Sections</span></summary><div>'+links+'</div></details>'
  +'</div><span class="chapter-progress" aria-hidden="true"></span></nav>';
}
function budgetField(city,key){
 return '<label for="cost-'+key+'"><span>'+h(fieldLabels[key])+' <small class="muted">· '+(groupFields.has(key)?'For three':'Per adult')+'</small></span><input id="cost-'+key+'" type="number" min="0" max="150000" step="1" inputmode="numeric" data-cost="'+key+'" value="'+budget(city)[key]+'"></label>';
}
function paintCity() {
 closePresentation();
 const city = current;
 const editorial = book.editorial.cities[city.id];
 const photo = photograph(city, editorial.cover);
 const area = photograph(city, editorial.neighborhood);
 const extra = photograph(city, editorial.extra);
 const next = cities[(cities.indexOf(city) + 1) % cities.length];
 const f = city.flights || {};
 const transport = city.transport || {};
 el('city').innerHTML = '<div class="chapter chapter-'+city.id+'" id="chapter" style="--chapter-position:'+h(editorial.position)+'">'
  +'<div class="chapter-art" style="--preview:url('+book.previews[city.id]+')">'+imageMarkup(photo,'backdrop','')+'</div>'
  +'<div class="wrap chapter-inner"><p class="eyebrow">'+h(city.country)+' · '+h(clock(city))+'</p><h2 tabindex="-1">'+h(city.city)
  +'</h2><p class="chapter-line">'+h(editorial.headline)+'</p><p class="chapter-facts"><span>'+city.nights+' nights</span><span id="chapter-per-adult">'+money(total(city)/3)+' per adult</span><span id="chapter-group">'+money(total(city))+' for three</span></p></div><a class="chapter-credit" href="#photos-credit">'+h(photo.caption)+'</a></div>'
  +chapterNav(city)
  +'<section id="intro" class="arrival wrap" data-chapter-section><div><p class="eyebrow">Arrival in '+h(city.city)+'</p><h2 tabindex="-1">'
  +h(editorial.headline)+'</h2><p class="lede">'+h(editorial.intro)+'</p></div>'
  +'<div id="flight" class="arrival-facts"><p class="eyebrow">Flights from Medina</p>'+flightLeg('Outbound',f.out)
  +flightLeg('Return',f.back)+'<p class="small">'+h(f.status||'Published schedules; checkout not verified')
  +'</p><details class="flight-details"><summary>Entry, weather and booking</summary><p>'+h(city.entry)+'</p><p>'+h(city.winter)+' '+h(city.light)
  +'</p><p>'+h(f.bags||'Baggage depends on fare family; price at checkout.')+'</p><p>'+h(f.note)+'</p><p class="small">'
  +(f.links||[]).map(l=>external(l.url,l.label)).join(' · ')+'</p></details></div></section>'
  +section('stays','Stays','<p class="section-lead">Two stays for three adults. Check room photos and winter outdoor access in each listing.</p>'
   +'<div class="stays">'+city.stays.map(stayCard).join('')+'</div>'
   +outdoorShortlist(city)
   +(city.alternatives?.length?'<details class="rule"><summary>Other stays</summary><p>'+city.alternatives.map(a=>external(a.url,a.name||a.label)
    +' · '+h([a.notes||a.note,a.status].filter(Boolean).join(' · ')||'Check dates, beds and total')).join('<br>')+'</p></details>':'')
   +'<a href="#walk" data-jump="walk" class="text-link" id="walk-jump"></a>')
  +'<figure class="wrap neighborhood-photo" data-scroll-picture>'+imageMarkup(area)+'<figcaption class="small">From the photo journal · '+photoCredit(area)+'</figcaption></figure>'
  +section('walk','Walks and transport','<div id="map"></div>'+ (transport.city?'<div class="transport-notes"><h3>Getting around</h3><dl>'
   +[['In the city',transport.city],['Airport transfer',transport.transfer],['Day trips',transport.day],['Short car hire',transport.rental]]
    .filter(([,v])=>v).map(([k,v])=>'<div><dt>'+h(k)+'</dt><dd>'+h(v)+'</dd></div>').join('')+'</dl></div>':''))
  +section('winter','Winter plans',winterMarkup())
  +section('itinerary','Itinerary','<p class="section-lead">Open a day for the stops, transit, meals and a fallback. Times and daily costs are estimates.</p>'
   +'<div class="itinerary-layout"><div class="daylist">'+city.days.map(dayMarkup).join('')+'</div>'
   +'<figure class="journey-photo" data-scroll-picture>'+imageMarkup(extra)+'<figcaption class="small">'+photoCredit(extra)+'</figcaption></figure></div>')
  +section('budget','Budget','<p class="section-lead">Costs for the full trip, in SAR.</p><div class="budget-layout"><aside class="budget-total" id="total" aria-live="polite"></aside><div><p class="small budget-help">Totals include contingency.</p><div class="budget-fields">'
   +budgetKeys.filter(key=>!carFields.has(key)).map(key=>budgetField(city,key)).join('')+'</div><details class="car-costs" '
   +(budgetKeys.some(key=>carFields.has(key)&&budget(city)[key])?'open':'')+'><summary>Car rental costs</summary><div class="budget-fields">'
   +budgetKeys.filter(key=>carFields.has(key)).map(key=>budgetField(city,key)).join('')+'</div></details></div></div>'
   +'<div class="budget-actions"><button class="action" data-reset>Reset city budget</button> <button class="action" data-print>Print itinerary</button></div>')
  +section('photos','Photos','<div id="gallery"></div>')
  +'<section class="chapter-end"><div class="wrap"><p class="eyebrow">The decision · '+h(city.city)
  +'</p><h2>What to weigh</h2><p class="lede">'+h(editorial.finish)+'</p><div class="end-actions">'
  +'<a class="cover-action" href="#compare">Compare trips <span aria-hidden="true">↘</span></a><button class="action" data-next-city="'
  +next.id+'">Next chapter · '+h(next.city)+' <span aria-hidden="true">→</span></button></div></div></section>';
 paintGallery();
 paintMap();
 paintTotal();
 if (window.IntersectionObserver) observeChapter();
 if (window.history) {
  const image = el('chapter').querySelector('img');
  image.decode().then(() => image.classList.add('is-ready'), () => {});
  const menu = document.querySelector('.chapter-menu');
  menu.addEventListener('toggle', () => {
   if (!menu.open) return;
   const menuPanel = menu.querySelector('div');
   const down = menu.getBoundingClientRect().bottom + menuPanel.offsetHeight;
   menu.classList.toggle('opens-up', down > window.innerHeight - 8);
  });
 }
}
function flightLeg(label, value) {
 const [date, carrier, route, timing] = string(value).split(' · ');
 return '<div class="flight-leg"><div><b>'+h(label)+'</b><span>'+h(date)+' · '+h(carrier)+'</span></div>'
  +'<strong>'+h(route)+'</strong><small>'+h(timing)+' · Local times</small></div>';
}
function dayMarkup(day, index) {
 return '<details class="day" '+(index === 0 ? 'open' : '')+'><summary><span>'+h(Number(day.date.slice(8))+' Dec')
  +'</span><strong>'+h(day.title)+'</strong></summary><div class="day-body"><ol class="stops">'+(day.stops||[]).map(stop =>
    '<li><strong>'+h(stop.time)+' · '+h(stop.name)+'</strong><br><span class="small">'+h([stop.duration,stop.mode,stop.travel].filter(Boolean).join(' · '))
    +'</span> '+h(stop.note)+'</li>').join('')+'</ol><p><b>Meals</b> · '+h(day.meal)+' <strong>'+money(day.cost)
  +' per adult</strong> for the day.</p><p class="small"><b>Alternative</b> · '+h(day.backup)+'</p></div></details>';
}
function providerDirections(anchor, route) {
 const origin = encodeURIComponent(anchor.start.join(','));
 const destination = encodeURIComponent(route.point.join(','));
 const google = 'https://www.google.com/maps/dir/?api=1&origin='+origin+'&destination='+destination+'&travelmode=walking';
 const apple = 'https://maps.apple.com/directions?source='+origin+'&destination='+destination+'&mode=walking';
 return '<div class="walk-actions">'+external(google,'Open in Google Maps','action walk-google')
  +external(apple,'Apple Maps','action')+'</div>';
}
function walkBackdrop(scene, xy) {
 if (!scene) return '';
 const [west,south,east,north] = scene.bbox;
 const [left,top] = xy([north,west]), [right,bottom] = xy([south,east]);
 return '<img class="walk-basemap" src="'+h(scene.data)+'" alt="" loading="lazy" decoding="async" width="'+scene.width
  +'" height="'+scene.height+'" style="left:'+left/6+'%;top:'+top/3.5+'%;width:'+(right-left)/6+'%;height:'+(bottom-top)/3.5+'%">';
}
function walkModes(mode) {
 return '<div class="walk-modes" role="group" aria-label="Map background">'
  +[['satellite','Satellite'],['diagram','Diagram']].map(([style,label])=>'<button type="button" class="action" data-walk-style="'+style
   +'" aria-pressed="'+(style===mode)+'">'+label+'</button>').join('')+'</div>';
}
function walkProjection(anchor, route, scene) {
 const points = [anchor.start, ...(route ? [route.point, ...(route.path || [])] : [])];
 const lat = points.map(p => p[0]), lon = points.map(p => p[1]);
 const south = Math.min(...lat), north = Math.max(...lat);
 const west = Math.min(...lon), east = Math.max(...lon);
 const cosine = Math.cos(anchor.start[0] * Math.PI / 180);
 const scale = Math.min(456 / Math.max((east - west) * cosine, .0017), 235 / Math.max(north - south, .0011));
 let cx = (west + east) / 2, cy = (south + north) / 2;
 if (scene) {
  const [left,bottom,right,top] = scene.bbox;
  const halfWidth = 300 / scale / cosine, halfHeight = 175 / scale;
  cx = Math.max(left + halfWidth, Math.min(right - halfWidth, cx));
  cy = Math.max(bottom + halfHeight, Math.min(top - halfHeight, cy));
 }
 return {xy: p => [300 + (p[1] - cx) * cosine * scale, 175 - (p[0] - cy) * scale], scale};
}
function walkScale(scale) {
 const pixelsPerMeter = scale / 111195;
 const meters = [1000,500,250,100,50,25].find(m => m * pixelsPerMeter <= 124) || 25;
 const end = (21 + meters * pixelsPerMeter).toFixed(1);
 return '<path class="walk-scale" d="M21 328v5H'+end+'v-5"/><text x="21" y="324" class="map-label">'
  +(meters>=1000?'1 km':meters+' m')+'</text>';
}
function walkLeaders(anchor, route, xy, scale) {
 const path = route?.path;
 if (!path?.length) return '';
 return [[anchor.start,path[0]],[route.point,path.at(-1)]].map(([point,nearest]) => {
  const [x,y]=xy(point), [nx,ny]=xy(nearest);
  if (Math.hypot(x-nx,y-ny) * 111195 / scale < 12) return '';
  return '<path class="walk-leader" d="M'+x+','+y+'L'+nx+','+ny+'"/>';
 }).join('');
}
const shortWalkNames = {
 'Danube promenade at Széchenyi Square': 'Széchenyi Square promenade',
 'Danube Island path access near Reichsbrücke': 'Danube Island at Reichsbrücke'
};
function syncWalkList() {
 const list = el('map').querySelector('.walk-list-disclosure');
 if (list) list.open = !compactWalks?.matches || walkListExpanded;
}
function paintMap(){
 const map=book.maps[current.id], node=el('map');
 if(!map?.anchors?.length){node.textContent='No verified walks for this city.';return;}
 const previousList = compactWalks?.matches && node.querySelector('.walk-list-disclosure');
 if (previousList) walkListExpanded = previousList.open;
 const selected=current.stays[state.stays?.[current.id]??0];
 const matched=map.anchors.find(a=>a.stays?.includes(String(selected?.id)));
 const anchor=map.anchors.find(a=>a.id===anchorId)||matched||map.anchors.find(a=>!a.stays.length)||map.anchors[0];
 const routes=anchor.routes||[];
 const route=routes[routeIndex]||routes[0];
 const scene=book.basemaps[current.id];
 const mapMode=scene && state.walkMap!=='diagram'?'satellite':'diagram';
 const {xy,scale}=walkProjection(anchor,route,scene);
 const leaders=walkLeaders(anchor,route,xy,scale);
 const dot=(p,fill,size)=>{const [x,y]=xy(p);return '<circle cx="'+x+'" cy="'+y+'" r="'+size+'" fill="'+fill+'" stroke="#fff" stroke-width="2"/>';};
 const pin=(point, letter, direction, color)=>{
  const [x,y]=xy(point), dx=direction*18, dy=direction*16;
  return dot(point,color,7)+'<path d="M'+x+','+y+'l'+dx+','+dy+'" fill="none" stroke="'+color+'"/>'
   +'<text class="walk-pin" x="'+(x+dx+direction*6)+'" y="'+(y+dy+6)+'" text-anchor="'+(direction<0?'end':'start')+'">'+letter+'</text>';
 };
 const poly=r=>r.path?.length>1?'<polyline points="'+r.path.map(p=>xy(p).map(x=>x.toFixed(2)).join(',')).join(' ')+'" class="active-route"/>':'';
 const connector=(r)=>{const [x,y]=xy(anchor.start),[dx,dy]=xy(r.point);return '<line x1="'+x+'" y1="'+y+'" x2="'+dx+'" y2="'+dy+'" stroke="#7c3822" stroke-dasharray="5 5" stroke-width="2"/>';};
 const districtExample = ['budapest','vienna'].includes(current.id) && matched && matched === map.anchors[1];
 const caveat=anchor===matched?(districtExample?'District hub example. Travel from the apartment to this hub is unverified.':'Public starting point for the selected stay.'):matched?
  'City reference walk from a different starting point.':'No starting point was confirmed for the selected stay. These are city reference walks.';
 el('walk-jump').innerHTML=(matched&&!districtExample?'See walks from the public starting point':'See city reference walks')+' <span aria-hidden="true">↓</span>';
 const anchorPicker='<div class="anchor-picker"><label for="anchor-select">Walking from</label><select id="anchor-select" aria-describedby="walk-anchor-note">'+map.anchors.map(a=>'<option value="'+h(a.id)+'" '+(a===anchor?'selected':'')+'>'+h(a.name)+'</option>').join('')+'</select></div>';
 const routeDetails='<div id="route-note" aria-live="polite">'+(route?
  '<div class="walk-route-summary"><div><span class="eyebrow">Selected walk</span><strong>'+h(route.name)
   +'</strong></div><div class="route-time">'+(route.min==null?'Time unavailable':(route.estimated?'≈ ':'')+h(route.min)+' min · '+h(route.km)+' km')
   +'<small>Estimated walk</small></div></div><p class="small walk-from">A · '+h(anchor.name)+' <span>→ B · '+h(route.name)+'</span></p>':'No route calculated')+'</div>';
 const diagram='<div class="mapbox" data-walk-map="'+mapMode+'">'+walkBackdrop(scene,xy)+'<svg viewBox="0 0 600 350" role="img" aria-label="'+h('Walk from '+anchor.name+(route?' to '+route.name:''))+'"><defs><pattern id="grid" width="27" height="27" patternUnits="userSpaceOnUse"><path d="M27 0H0V27" stroke="#c8cfb7" fill="none" opacity=".55"/></pattern></defs><rect class="walk-grid" width="600" height="350" fill="url(#grid)"/><text x="546" y="32" class="map-label">N ↑</text>'+walkScale(scale)+leaders+(route?(poly(route)||connector(route)):'')+pin(anchor.start,'A',-1,'#194637')+(route?pin(route.point,'B',1,'#a45226'):'')+'</svg></div>';
 const quickWalk='<label class="quick-walk" for="route-select">Choose a walk <select id="route-select">'+routes.map((r,i)=>
  '<option value="'+i+'"'+(r===route?' selected':'')+'>'+h(Object.hasOwn(shortWalkNames,r.name)?shortWalkNames[r.name]:r.name)+'</option>').join('')+'</select></label>';
 node.innerHTML='<div class="route-layout"><div class="walk-picker-rail">'+anchorPicker+quickWalk+'</div>'
  +'<div class="map-stage">'+routeDetails+'<div class="walk-visual-group">'+(scene?walkModes(mapMode):'')+diagram+'</div>'
  +'<div class="walk-reference"><p class="small walk-anchor-note" id="walk-anchor-note" aria-live="polite"><b>'+h(caveat)+'</b> '+h(anchor.note||'')+'</p>'
  +(leaders?'<p class="small walk-connection">Dotted lines connect public pins to the routed path.</p>':'')
  +(route?providerDirections(anchor,route):'')
  +'<p class="small walk-provider-note">'+h(map.attribution||'© OpenStreetMap contributors')+' · Google and Apple may choose a different path.'
  +(scene?' <span class="walk-scene-credit">Contains modified Copernicus Sentinel data '+h(scene.date.slice(0,4))+' · '+external(scene.source,'Scene '+scene.date)+'.</span>':'')+'</p></div></div>'
  +'<details class="walk-list-disclosure"'+(!compactWalks?.matches||walkListExpanded?' open':'')+'><summary>All walk times</summary>'
  +'<div class="walking-list">'+routes.map((r,i)=>'<button class="route-toggle" data-route="'+i+'" aria-pressed="'+(r===route)+'"><strong>'+h(r.name)+'</strong><small>'+(r.min==null?'Walk time unavailable':(r.estimated?'~':'')+h(r.min)+' min · '+(r.estimated?'~':'')+h(r.km)+' km'+(r.estimated?' · estimate':''))+'</small></button>').join('')+'</div></details></div>';
}
function paintTotal() {
 const sum = total(current);
 const person = money(sum / 3);
 const group = money(sum);
 const status = sum / 3 > 6000 ? 'Above the target' : sum / 3 < 4000 ? 'Below the target' : 'Within the target';
 el('total').innerHTML = '<div class="budget-total-amounts">'
  +'<div class="budget-total-amount"><span class="meta">Per adult</span><strong id="total-person">'+person+'</strong></div>'
  +'<div class="budget-total-amount"><span class="meta">Total for three</span><strong id="total-group">'+group+'</strong></div>'
  +'</div><p class="small budget-total-status">'+status+'</p>';
 el('chapter-per-adult').textContent = person+' per adult';
 el('chapter-group').textContent = group+' for three';
}
function revealBudgetFocus(control) {
 requestAnimationFrame(() => {
  if (document.activeElement !== control) return;
  const bounds = control.getBoundingClientRect();
  const blockers = [document.querySelector('.mast'), document.querySelector('.city-subnav'), el('total')];
  const visibleTop = blockers.reduce((edge, blocker) => {
   const rect = blocker.getBoundingClientRect();
   const style = getComputedStyle(blocker);
   const overlaps = rect.left < bounds.right && rect.right > bounds.left;
   const pinned = style.position === 'sticky' && rect.top <= parseFloat(style.top) + 1;
   return overlaps && pinned ? Math.max(edge,rect.bottom) : edge;
  }, 0) + 8;
  if (bounds.top < visibleTop) window.scrollBy({top:bounds.top-visibleTop,behavior:'instant'});
 });
}
function compactOutdoor(stay) {
 const outdoor = stayOutdoor(stay);
 if (outdoor.kind === 'private' && /balcony/i.test(outdoor.label)) return 'Private balcony';
 if (outdoor.kind === 'nearby') return 'Park nearby · private unverified';
 if (outdoor.kind === 'unknown') return 'Outdoor unverified';
 if (outdoor.kind === 'listed' && /rooftop/i.test(outdoor.label)) return 'Roof terrace · confirm access';
 return outdoor.label;
}
function compareOptions(selected){return cities.map(c=>'<option value="'+c.id+'" '+(c.id===selected?'selected':'')+'>'+h(c.city)+'</option>').join('');}
const comparePrices = {
 person: ['Per adult',c=>money(total(c)/3)],
 group: ['For three',c=>money(total(c))],
 stay: ['Stay',c=>money(budget(c).stay)],
 food: ['Meals each',c=>money(budget(c).food)],
 transit: ['Local travel each',c=>money(budget(c).transit)],
 outdoor: ['Outdoor space',c=>compactOutdoor(c.stays[state.stays?.[c.id]??0])]
};
function refreshPrices(){
 el('pick-price-'+current.id).textContent=money(total(current)/3);
 const A=byId[state.left]||cities[0], B=byId[state.right]||cities[1];
 [A,B].forEach((city,i)=>{
  if(city===current) for(const [key,[,price]] of Object.entries(comparePrices)) el('compare-'+i+'-'+key).textContent=price(city);
 });
 refreshCompareBars(A,B);
}
function paintCompare(){
 const A=byId[state.left]||cities[0], B=byId[state.right]||cities[1];
 const prices=Object.entries(comparePrices).map(([key,[label,price]])=>[label,price,key]);
 const items=[...prices.slice(0,2),['Dates',clock],['Nights',c=>c.nights],...prices.slice(2)];
 const details=[['Outbound',c=>string(c.flights?.out)],['Return',c=>string(c.flights?.back)],['Entry',c=>c.entry],['Winter',c=>c.winter]];
 const rows=list=>list.map(([label,get,key])=>'<tr><th scope="row">'+h(label)+'</th>'+[A,B].map((city,i)=>'<td'+(key?' id="compare-'+i+'-'+key+'"':'')+'>'+h(get(city))+'</td>').join('')+'</tr>').join('');
 const head='<thead><tr><th scope="col">Trip detail</th><th scope="col">'+h(A.city)+'</th><th scope="col">'+h(B.city)+'</th></tr></thead>';
 const container=el('compare'), expanded=container.querySelector('.compare-details')?.open;
 container.innerHTML='<p class="eyebrow">The shortlist</p><h2>Compare trips</h2><p class="section-lead">Choose two cities. Edit budgets to update the estimates.</p><div class="compare-controls"><label for="left-city">First city<select id="left-city">'+compareOptions(A.id)+'</select></label><label for="right-city">Second city<select id="right-city">'+compareOptions(B.id)+'</select></label></div>'+compareBudgetBars(A,B)+'<div class="compare-scroll"><table>'+head+'<tbody>'+rows(items)+'</tbody></table></div><details class="compare-details" '+(expanded?'open':'')+'><summary>Flights, entry and winter weather</summary><div class="compare-depth">'+details.map(([label,get])=>'<section><h3>'+h(label)+'</h3><dl>'+[A,B].map(city=>'<div><dt>'+h(city.city)+'</dt><dd>'+h(get(city))+'</dd></div>').join('')+'</dl></section>').join('')+'</div></details>';
}
function evidenceActions(...links) {
 return '<div class="source-actions">'+links.map(([url,label])=>external(url,label,'source-action')).join('')+'</div>';
}
function paintEvidence() {
 const citySources = cities.map(c=>'<details><summary>'+h(c.city)+' sources</summary><p class="small">Earlier estimate for three: '
  +h(c.priorTotal)+'.</p><ul class="source-list">'+(c.sources||[]).map(s=>'<li>'+evidenceActions([s.url,s.label||s.name||s.url])
   +'<p class="small">'+h([s.status,s.checked,s.note].filter(Boolean).join(' · '))+'</p></li>').join('')+'</ul></details>').join('');
 const photos = cities.flatMap(city=>book.photos[city.id].map(photo=>'<li><p>'+h(photo.caption)+' · '+h(photo.author)
  +(photo.modifications?' · '+h(photo.modifications):'')+'</p>'+evidenceActions([photo.url,'Photo source'],[photo.licenseUrl,photo.license])+'</li>')).join('');
 const methods = [
  ['Walks','The offline guide includes routed paths and clearly labeled estimates. Estimated times use straight-line distance × 1.37 and an assumed 3.6 km/h. Crossings, grades and weather may change the time.',
   ['https://www.openstreetmap.org/copyright','OpenStreetMap attribution'],['https://valhalla.github.io/valhalla/','Valhalla routing']],
  ['Atlas','The atlas connects Medina airport to approximate city centers. Globe arcs and distances use a spherical great circle. The map shows straight bearings on its projection. See Arrival for each flight.',
   ['https://www.naturalearthdata.com/about/terms-of-use/','Natural Earth'],['https://ourairports.com/airports/OEMA/','OurAirports (MED)']],
  ['Currency','The calculator sums SAR inputs. Earlier examples were rounded during the 23 November 2026 research. The Saudi Central Bank keeps an exchange-rate archive. The guide uses no live currency conversion.',
   ['https://www.sama.gov.sa/en-us/currency/finexc/pages/currency.aspx','Saudi Central Bank FX reference']]
 ];
 el('evidence').innerHTML = '<h2>Sources</h2><p class="section-lead">Stay prices were observed on 23 November 2026. Flight times follow published schedules. Confirm both before booking.</p>'
  +citySources+'<details id="photos-credit"><summary>Photography credits</summary><ul class="source-list">'+photos+'</ul></details>'
  +'<details><summary>Routes, atlas and currency</summary><div class="source-methods">'+methods.map(([title,copy,...links])=>'<section><h3>'+h(title)
   +'</h3><p class="small">'+h(copy)+'</p>'+evidenceActions(...links)+'</section>').join('')+'</div></details>';
}
function setChapterSection(sectionId) {
 const label = chapterLinks.find(([id])=>id===sectionId)?.[1];
 const summary = document.querySelector('.chapter-menu summary');
 const visible = label ? 'Sections · '+label : 'Sections';
 summary.querySelector('.chapter-menu-current').textContent = visible;
 summary.setAttribute('aria-label',visible+' in '+current.city);
 for (const link of document.querySelectorAll('.city-subnav [data-jump]')) {
  if (link.dataset.jump === sectionId) link.setAttribute('aria-current','location');
  else link.removeAttribute('aria-current');
 }
}
function jumpTo(sectionId) {
 const section = el(sectionId);
 if (window.history) setChapterSection(sectionId);
 section.querySelector('h2')?.focus({preventScroll:true});
 section.scrollIntoView({block:'start'});
}
function visitCity(id, section = 'chapter', record = true) {
 if (!byId[id]) return;
 current = byId[id];
 state.city = id;
 anchorId = '';
 routeIndex = 0;
 walkListExpanded = false;
 slide = 0;
 winterChoice = 0;
 persist();
 paintPick();
 paintCity();
 if (window.history) {
  if (record) writeChapterHash(section);
  if (atlasGlobe) useMap();
  previewDestination(id);
 }
 jumpTo(section);
}
function writeChapterHash(section) {
 const hash = '#' + current.id + (section === 'chapter' ? '' : '/' + section);
 if (window.location.hash !== hash) window.history.pushState(null, '', hash);
}
function observeChapter() {
 chapterObserver?.disconnect();
 const sections = [...document.querySelectorAll('[data-chapter-section]')];
 const bars = document.querySelector('.mast').offsetHeight + document.querySelector('.city-subnav').offsetHeight;
 const cue = Math.min(window.innerHeight-2,Math.max(bars+18,Math.round(window.innerHeight*.3)));
 chapterObserver = new IntersectionObserver(() => {
  const active = sections.find(section => {
   const rect = section.getBoundingClientRect();
   return rect.top <= cue+1 && rect.bottom > cue;
  });
  if (active || sections[0].getBoundingClientRect().top > cue) setChapterSection(active?.id);
 }, {rootMargin:'-'+cue+'px 0px -'+(window.innerHeight-cue-2)+'px 0px'});
 sections.forEach(section => chapterObserver.observe(section));
}
function restoreChapterLocation() {
 const [id, section] = pageLocation();
 if (byId[id]) visitCity(id, section && el(section) ? section : 'chapter', false);
}
document.addEventListener('click',e=>{
 if (window.history && !e.target.closest('.chapter-menu')) {
  const menu = document.querySelector('.chapter-menu[open]');
  if (menu) menu.open = false;
 }
 const link = e.target.closest('a[data-jump],a[href="#photos-credit"]');
 if (window.history && link?.dataset.jump && !e.metaKey && !e.ctrlKey && !e.shiftKey && !e.altKey) {
  e.preventDefault();
  document.querySelector('.chapter-menu').open = false;
  writeChapterHash(link.dataset.jump);
  jumpTo(link.dataset.jump);
  return;
 }
 if (link?.hash === '#photos-credit') el('photos-credit').open = true;
 const b=e.target.closest('button');if(!b)return;
 if(b.dataset.winterOption!==undefined) selectWinter(Number(b.dataset.winterOption));
 if(b.dataset.winterFilm) openPresentation(b.dataset.winterFilm,b);
 if(b.dataset.walkStyle) {
  state.walkMap=b.dataset.walkStyle;
  persist();
  el('map').querySelector('.mapbox').dataset.walkMap=state.walkMap;
  for (const toggle of el('map').querySelectorAll('[data-walk-style]')) {
   toggle.setAttribute('aria-pressed',String(toggle.dataset.walkStyle===state.walkMap));
  }
 }
 if(b.hasAttribute('data-winter-close')) dismissPresentation();
 if(b.dataset.city || b.dataset.nextCity || b.hasAttribute('data-open-preview')) visitCity(b.dataset.city || b.dataset.nextCity || previewId);
 if(b.dataset.route!==undefined) {
  routeIndex=Number(b.dataset.route);
  paintMap();
  el('map').querySelector('[data-route][aria-pressed=true]')?.focus({preventScroll:true});
 }
 if(b.dataset.gallery){const length=book.photos[current.id].length;slide=(slide+Number(b.dataset.gallery)+length)%length;paintGallery();el(el('photo-dialog').open?'photo-dialog':'gallery').querySelector('[data-gallery="'+b.dataset.gallery+'"]')?.focus({preventScroll:true});}
 if(b.hasAttribute('data-photo-open') || b.dataset.winterPhoto) {
  if (b.dataset.winterPhoto) {
   slide=book.photos[current.id].findIndex(photo=>photo.file===b.dataset.winterPhoto);
   paintGallery();
  }
  lastPhotoTrigger = b;
  paintPhotoDialog();
  el('photo-dialog').showModal();
 }
 if(b.hasAttribute('data-photo-close')) el('photo-dialog').close();
 if(b.dataset.stay!==undefined){
  const i=Number(b.dataset.stay), stay=current.stays[i];
  state.stays={...state.stays,[current.id]:i};
  state.budgets={...state.budgets,[current.id]:{...state.budgets?.[current.id],stay:stay.price||budget(current).stay}};
  persist();
  if (window.history) {
   for (const button of el('stays').querySelectorAll('[data-stay]')) {
    const selected = button === b;
    button.setAttribute('aria-pressed',String(selected));
    button.textContent = selected?'Stay selected':'Use this stay';
   }
   b.focus({preventScroll:true});
  } else el('stays').querySelector('.stays').innerHTML=current.stays.map(stayCard).join('');
  el('cost-stay').value=budget(current).stay;
  anchorId='';routeIndex=0;paintMap();paintTotal();refreshPrices();
 }
 if(b.hasAttribute('data-reset')){if(state.budgets)delete state.budgets[current.id];if(state.stays)delete state.stays[current.id];anchorId='';routeIndex=0;persist();paintCity();el('budget').querySelector('[data-reset]').focus({preventScroll:true});refreshPrices();}
 if(b.hasAttribute('data-print'))window.print();
});
document.addEventListener('input',e=>{const key=e.target.dataset.cost;if(!key)return;state.budgets={...state.budgets,[current.id]:{...state.budgets?.[current.id],[key]:n(e.target.value)}};persist();paintTotal();refreshPrices();});
function updateWalkPicker(controlId) {
 paintMap();
 const control = el(controlId);
 control.focus({preventScroll:true});
 if (shortLandscapeWalks?.matches) control.closest('.route-layout').scrollIntoView({block:'start',behavior:'instant'});
 else if (compactWalks?.matches && controlId === 'route-select' && el('map').querySelector('.mapbox').getBoundingClientRect().bottom > window.innerHeight) {
  control.closest('.quick-walk').scrollIntoView({block:'start',behavior:'instant'});
 }
}
document.addEventListener('focusin',e=>{
 if (window.history && e.target.matches('#budget input, #budget summary, #budget button')) revealBudgetFocus(e.target);
});
document.addEventListener('change',e=>{
 if(e.target.dataset?.cost)e.target.value=budget(current)[e.target.dataset.cost];
 if(e.target.id==='anchor-select'){anchorId=e.target.value;routeIndex=0;updateWalkPicker('anchor-select');}
 if(e.target.id==='route-select'){routeIndex=Number(e.target.value);updateWalkPicker('route-select');}
 if(e.target.id==='left-city'||e.target.id==='right-city'){state[e.target.id.split('-')[0]]=e.target.value;persist();paintCompare();el(e.target.id)?.focus({preventScroll:true});}
});
let printedDays=[];
window.addEventListener('beforeprint',()=>{printedDays=[...document.querySelectorAll('.day:not([open])')];printedDays.forEach(d=>d.open=true);});
window.addEventListener('afterprint',()=>{printedDays.forEach(d=>d.open=false);printedDays=[];});
function bootGuide() {
 paintPick();
 paintCity();
 paintCompare();
 paintEvidence();
 if (!window.history) return;
 bootAtlas();
 const dialog = el('photo-dialog');
 dialog.addEventListener('close', () => {
  (lastPhotoTrigger?.isConnected ? lastPhotoTrigger : el('gallery').querySelector('[data-photo-open]'))?.focus({preventScroll:true});
 });
 dialog.addEventListener('keydown', event => {
  if (!['ArrowLeft','ArrowRight'].includes(event.key)) return;
  event.preventDefault();
  dialog.querySelector('[data-gallery="'+(event.key==='ArrowLeft'?'-1':'1')+'"]').click();
 });
 document.addEventListener('keydown', event => {
  if (event.key !== 'Escape' || dialog.open) return;
  if (event.target.closest('#winter-briefings') && !el('winter-film').hidden) {
   dismissPresentation();
   return;
  }
  const menu = document.querySelector('.chapter-menu[open]');
  if (menu) {
   menu.open = false;
   menu.querySelector('summary').focus();
  }
 });
 window.addEventListener('hashchange', restoreChapterLocation);
 if (window.IntersectionObserver) window.addEventListener('resize', observeChapter);
 compactWalks?.addEventListener('change',syncWalkList);
 el('city').addEventListener('toggle',event=>{
  if (compactWalks?.matches && event.target.matches('.walk-list-disclosure')) walkListExpanded=event.target.open;
 },true);
 if (byId[pageLocation()[0]]) requestAnimationFrame(restoreChapterLocation);
}
