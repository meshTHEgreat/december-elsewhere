function guidedMarkup(city) {
 const choices = book.guided.cities[city.id];
 const options = [['day', 'Day trip'], ['night', 'Stay overnight']].map(([key, label]) => {
  const plan = choices[key];
  const selected = key === choices.preferred;
  return '<details name="guided-option" class="guided-option" data-guide-plan="'+key+'"'+(selected?' open':'')+'>'
   +'<summary><span>'+label+'<small>'+h(plan.time)+'</small></span></summary><div class="guided-body"><h3>'+h(plan.title)
   +'</h3><ol class="guided-journey" aria-label="Suggested journey">'+plan.journey.map(stop=>'<li>'+h(stop)+'</li>').join('')
   +'</ol><p>'+h(plan.guide)+'</p><p class="guided-check">'+h(plan.check)+'</p><div class="guided-links">'
   +plan.links.map(([text,url])=>external(url,text,'source-action')).join('')+'</div></div></details>';
 }).join('');
 return '<details class="guided-outings" id="guides"><summary>Local guides <small>Day trip or overnight?</small></summary>'
  +'<div class="guided-plans"><p class="guided-pick">'+h(choices.pick)+'</p>'+options
  +'<p class="small guided-cost">Availability and prices for your dates are unconfirmed. Ask where the guide is based, which stops are guided, and what the total covers for three. If an overnight replaces a city night, update lodging and transport without counting them twice.</p>'
  +'<a class="text-link" href="#budget" data-jump="budget">Update the budget</a><p class="small">Listings checked '+h(book.guided.checked)+'.</p></div></details>';
}
