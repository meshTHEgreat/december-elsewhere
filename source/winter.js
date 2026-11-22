let winterChoice = 0;
let presentationUnmount;
let presentationTrigger;
let presentationRequest = 0;

function winterOptions() { return book.winter[current.id].options; }
function winterLinks(option) {
 return option.links.map(([label, url]) => external(url, label, 'winter-source')).join('');
}
function winterMarkup() {
 const winter = book.winter[current.id];
 const options = winter.options;
 const tabs = options.length > 1 ? '<div class="winter-options" role="group" aria-label="Winter options">'
   + options.map((option, index) => '<button data-winter-option="'+index+'" class="winter-option" aria-pressed="'+(index===winterChoice)+'">'
     +'<span>'+h(option.title)+'</span><small>'+h(option.tag)+'</small></button>').join('') + '</div>' : '';
 return '<div class="winter-heading"><p class="eyebrow">'+h(current.city)+' · Winter field guide</p><p class="lede">'
   +h(winter.title)+'</p><p class="section-lead">'+h(winter.summary)+'</p></div>'
   + tabs + '<div id="winter-choice">'+winterOptionMarkup(options[winterChoice])+'</div>'
   + '<div class="winter-briefings" id="winter-briefings"><div><p class="eyebrow">Visual briefings</p><h3>See the plan in motion</h3>'
   + '<p class="small">Short visual guides. The trip facts and links are available above.</p></div><div class="winter-film-buttons">'
   + '<button class="action" data-winter-film="baku">Caspian to Caucasus <span aria-hidden="true">▷</span></button>'
   + '<button class="action" data-winter-film="overview">Winter across the five <span aria-hidden="true">▷</span></button></div>'
   + '<div class="winter-film-message" role="status" id="winter-film-message"></div>'
   + '<div id="winter-film" class="winter-film" hidden><div id="winter-film-stage"></div>'
   + '<button class="action winter-close" data-winter-close type="button">Close preview</button></div></div>';
}
function winterOptionMarkup(option) {
 const photo = photograph(current, option.photo);
 return '<div class="winter-option-layout"><figure class="winter-figure"><button class="photo-open" data-winter-photo="'+h(photo.file)
  +'" aria-label="View photo full screen: '+h(photo.title)+'">'+imageMarkup(photo)+'<span aria-hidden="true">↗</span></button>'
  +'<figcaption class="small">'+photoCredit(photo, true)+'</figcaption></figure>'
  +'<div class="winter-option-facts"><p class="eyebrow">'+h(option.area)+'</p><h3>'+h(option.title)+'</h3>'
  +'<p class="winter-status">'+h(option.status)+'</p><div class="winter-route"><span class="eyebrow">Route outline</span><strong>'
  +h(option.journey)+'</strong><small>'+h(option.time)+'</small></div>'
  +'<p>'+h(option.conditions)+'</p>'+(option.ideas.length?'<ul>'+option.ideas.map(idea=>'<li>'+h(idea)+'</li>').join('')+'</ul>':'')
  +(option.check?'<p class="winter-check">'+h(option.check)+'</p>':'')
  +'<div class="winter-official"><p class="eyebrow">Official links</p>'+winterLinks(option)
  +'<p class="small">Sources checked '+h(book.winter.checked)+'.</p></div></div></div>';
}
function selectWinter(index) {
 const option = winterOptions()[index];
 if (!option) return;
 winterChoice = index;
 el('winter-choice').innerHTML = winterOptionMarkup(option);
 for (const button of el('winter').querySelectorAll('[data-winter-option]')) {
  button.setAttribute('aria-pressed', String(Number(button.dataset.winterOption) === index));
 }
}
function presentationStory(mode) {
 const regional = mode === 'baku';
 const entries = regional
   ? book.winter.baku.options.map(option => ({city: byId.baku, option}))
   : cities.map(city => ({ city, option: book.winter[city.id].options[0] }));
 return {label: regional ? 'Caspian to Caucasus' : 'Winter across the five',
  frames: entries.map(({city, option}) => ({
   title: regional ? option.title : city.city,
   area: option.area,
   note: option.filmNote,
   src: photograph(city, option.filmPhoto || option.photo).data
  }))};
}
function closePresentation() {
 presentationRequest++;
 presentationUnmount?.();
 presentationUnmount = undefined;
 if (!window.history) return;
 const panel = el('winter-film');
 if (panel) panel.hidden = true;
 const status = el('winter-film-message');
 if (status) status.textContent = '';
}
function dismissPresentation() {
 closePresentation();
 presentationTrigger?.focus({preventScroll:true});
}
async function openPresentation(mode, trigger) {
 closePresentation();
 presentationTrigger = trigger;
 const request = presentationRequest;
 const status = el('winter-film-message');
 status.textContent = 'Loading visual briefing';
 trigger.setAttribute('aria-busy', 'true');
 try {
  const runtime = await loadGuideModule('winter-stage-code','DecemberWinterStage');
  if (request !== presentationRequest) return;
  const panel = el('winter-film');
  panel.hidden = false;
  presentationUnmount = runtime.mount(el('winter-film-stage'), presentationStory(mode));
  status.textContent = '';
  panel.scrollIntoView({block:'nearest'});
 } catch {
  if (request === presentationRequest) status.textContent = 'The visual briefing could not load. The guide above is ready.';
 } finally {
  trigger.removeAttribute('aria-busy');
 }
}

function stayOutdoor(stay) {
 return book.outdoor.listings[stay.id] || {kind:'unknown',label:'Outdoor space unverified',note:'Ask whether outdoor space is attached to the unit.'};
}
function outdoorShortlist(city) {
 const picks = city.stays.filter(stay => stayOutdoor(stay).kind==='private');
 const listed = city.stays.find(stay => stayOutdoor(stay).kind==='listed');
 const extra = book.outdoor.alternatives[city.id];
 if (!picks.length && !listed && !extra) return '';
 const names = picks.map(stay=>stayOutdoor(stay).label).join(' · ');
 return '<aside class="outdoor-guide"><div><p class="eyebrow">For outdoor space</p><p>'
  +(picks.length?'Start with the options marked private. '+h(names)+'.':listed?
    'Start with '+h(listed.name)+'. Ask about private access and seating.':'The priced stays have no confirmed private outdoor space. See the additional listing below.')
  +'</p></div>'+(extra?'<div class="outdoor-extra"><strong>'+h(extra.title)+'</strong><p class="small">'+h(extra.note)
  +' · Rates and date availability unverified.</p>'+external(extra.url,'Open real listing photos','action')+'</div>':'')+'</aside>';
}

function compareBudgetBars(A, B) {
 const scale = Math.max(6000, total(A)/3, total(B)/3);
 const row = (city, index) => {
  const cost = total(city)/3;
  return '<div class="compare-budget-row"><div><b>'+h(city.city)+'</b><strong id="compare-mark-value-'+index+'">'+money(cost)+'</strong></div>'
   +'<div class="compare-budget-track" aria-hidden="true"><span class="compare-target"></span><span class="compare-marker" id="compare-mark-'+index
   +'" style="--marker:'+(cost/scale*100).toFixed(3)+'%"></span></div></div>';
 };
 return '<div class="compare-budget-visual" id="compare-budget-visual" style="--target-start:'+(4000/scale*100).toFixed(3)
  +'%;--target-end:'+(6000/scale*100).toFixed(3)+'%"><p class="eyebrow">Estimated per adult</p>'
  +row(A,0)+row(B,1)+'<p class="small">Shaded band: SAR 4,000–6,000 per adult</p></div>';
}
function refreshCompareBars(A, B) {
 const visual = el('compare-budget-visual');
 if (!visual?.style) return;
 const scale = Math.max(6000, total(A)/3, total(B)/3);
 visual.style.setProperty('--target-start', (4000/scale*100).toFixed(3)+'%');
 visual.style.setProperty('--target-end', (6000/scale*100).toFixed(3)+'%');
 [A,B].forEach((city,index) => {
  const cost=total(city)/3;
  el('compare-mark-value-'+index).textContent=money(cost);
  el('compare-mark-'+index).style.setProperty('--marker',(cost/scale*100).toFixed(3)+'%');
 });
}
