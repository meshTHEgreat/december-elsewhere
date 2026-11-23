# 01 | UI inventory

Baseline commit `6f017c5`. This inventory describes the shipped product and its source. All views are public. The guide has no account, admin area, authentication, database, sidebar, or backend. The only supported application language is English. The document declares `lang="en"` and uses the browser's default LTR direction. Sources and booking sites can have other languages. Those are outside the interface.

## Pages and links

| Address | What opens | Source and container |
| --- | --- | --- |
| Pages root `/december-elsewhere/` or `/december-elsewhere/index.html` | Cover, atlas, current destination, trip comparison, sources | `source/index.template`, `source/app.js`, `source/atlas.js`. One `main#main` |
| Pages download `/december-elsewhere/offline.html` or local `index.html` | The same guide with fonts, media and data embedded. The footer omits the download link. | `source/build.py`. The two offline files are identical. |
| `#main`, `#top`, `#destinations`, `#compare`, `#evidence`, `#photos-credit` | Native anchors for skip, cover, cities and atlas, trip comparison, sources, and photo credits. Activating a photo credit link opens its disclosure. | Native navigation in `source/index.template`, and `paintCompare`, `paintEvidence` and the click handler in `source/app.js` |
| `#baku`, `#tbilisi`, `#budapest`, `#vienna`, `#prague` | Destination cover. A city selection also updates the atlas preview. | `article#city` and `div#chapter.chapter`. `paintCity` and `visitCity` in `source/app.js` |
| `#<city>/intro`, `/stays`, `/walk`, `/winter`, `/itinerary`, `/budget`, `/photos` | Seven canonical section links for each city. These restore the chapter and focus the section heading. | `chapterLinks`, `writeChapterHash`, `restoreChapterLocation` and `jumpTo` in `source/app.js` |
| `#<city>/chapter`, `#<city>/flight`, unknown suffix | `/chapter` is an alias. `/flight` resolves to a nested arrival panel. An unknown suffix falls back to the city cover. | `restoreChapterLocation` checks rendered IDs. Only the seven canonical section links are exposed by the chapter nav. |

Booking, route provider and source links open independently of the guide. Google Maps and Apple Maps receive the same public endpoints. Neither is needed to render the local walk. The browser's print preview is another layout of the same document. No detail, confirmation or error page has a separate path.

## Areas and states

### Chrome and atlas

| Piece | Layout and shared components | States to cover |
| --- | --- | --- |
| Mast, skip and footer | `source/index.template`, `.mast`, `.skip`, `.footer .wrap`. Wordmark, Cities, Winter, Compare. Footer links return to the cover or atlas and link to the offline download in the hosted version. | Default, hover, keyboard focus, narrow mast, scroll, hosted and offline footer. |
| Cover | `section#top.hero > .wrap.hero-inner`. Full-width photo, `.cover-action`, cover facts and credit. | Image loaded, first paint, reduced motion, phone and landscape crop, credit link. |
| Destination navigation | `chapterNav` in `source/app.js`, `.city-subnav > .wrap.chapter-nav-inner`. Desktop `.chapter-jumps`, compact `details.chapter-menu`, progress line and All cities. | Seven item labels, active section, viewport-dependent direction of the compact menu, overflow in landscape, outside click, Escape and focus return. Tabs keep their selected city. |
| City list and preview | `section#destinations.pick > .wrap.atlas-layout`, `.city-list`, `.atlas-panel`. `paintPick` in `source/app.js`, `bootAtlas` and `previewDestination` in `source/atlas.js`. | Five city buttons update the open chapter. The separate atlas select only changes the preview. Test direct distance and Read city with all five selections. |
| Globe | Atlas SVG or lazy canvas in `.atlas-visual` plus on-map label buttons from `source/globe.js`. Geo components also style through `source/styles.css`. | Flat map initially, Loading globe with disabled action, View map after successful activation, motion or reduced-motion use, drag and keyboard labels, return to map, no WebGL and forced context loss. Leaving the atlas closes the canvas. Sample the availability messages below. |

### Destination chapters

| Piece | Layout and shared components | States to cover |
| --- | --- | --- |
| Intro photo and arrival | `paintCity` in `source/app.js`, full-width `.chapter` then `section#intro.arrival.wrap`. `.arrival-facts` and two `.flight-leg` rows. Copy from `source/editorial.json` and `source/travel-data.json`. | Five chapter crops, dates, nights and both prices. Entry, weather and booking collapsed/open. Both flight legs and status notes. |
| Stays | `#stays.section.wrap`; `stayCard`, `.stay`, `.stay-spec`, `.stay-cta`, `.rule` disclosure. The outdoor shortlist and labels come from `source/winter.js` and `source/outdoor-stays.json`. | Both stay selections, verified or unclear outdoor space, visible original listing link, alternate stays closed/open, budget and walk handoff, default/reset. |
| Neighborhood photograph | Standalone `figure.wrap.neighborhood-photo` between Stays and Walks. Image/caption factories in `source/app.js`, content from editorial and photo data. | Loaded and decoded, credits, motion and reduced motion. Vienna has a distinct rail width. |
| Walks and transport | `#walk.section.wrap`; `paintMap`, `.anchor-picker`, `.quick-walk`, `.route-layout`, `.map-stage`, `.walking-list`; below, `.transport-notes`. Styles split across `source/styles.css` and `source/winter.css`. | Two anchors per city, both stay-linked and city-example cases, choose walk, first and last route, satellite and diagram, return focus, Google and Apple URLs, pin and route discrepancy note, attribution, empty or unavailable texts. All 55 paths are current dataset states. |
| Winter plans | `#winter.section.wrap`; `winterMarkup` in `source/winter.js`, `.winter-options`, `.winter-option-layout`, `.winter-figure`, operator links. Uses `source/winter.css` and `source/winter-data.json`. | Five winter sections, eight total destinations/options, selected option, dated condition notes, external official checks, photo dialog entry. |
| Visual briefings | Shared `#winter-briefings` inside each chapter. `source/winter.js`, real Stageshow in `source/winter-stage.tsx`, `source/winter-stage.css` and bundled vendor modules. Inline preview, not a dialog. | Closed, loading, first/intermediate/last frame for both sequences, reduced-motion poster, failure, Close preview and Escape, focus return and chapter navigation cleanup. |
| Day by day | `#itinerary.section.wrap`; `dayMarkup`, `.itinerary-layout`, `.daylist`, `.day`, `.stops`, `.journey-photo` in `source/app.js` and `source/styles.css`. | First day open, others collapsed, each day expandable independently. Test all 37 days on activation and the print expansion/restoration state. |
| The photo journal | `#photos.section.wrap`; `paintGallery` and `galleryControls` use `.visual`, `.photo-open`, and `.gallery-tools`. Media and terms from `source/photography.json`. | Previous and next wrap at ends, count changes, photo credit and download, keyboard focus. All 24 photos are represented. |
| Photo dialog | Shared `dialog#photo-dialog` outside `main`. `paintPhotoDialog` uses `.lightbox-bar`, `.lightbox-figure`, and the same gallery controls as the inline view. | Open from journal and Winter, download, field of view on portrait and landscape, arrow keys, close button, Escape, focus return. No other modal/drawer. |
| What to weigh | `.chapter-end > .wrap`. Full-width dark editorial band and `.end-actions` in `paintCity`. | Compare trips, Next chapter, and Prague wraps to Baku. Five decision captions. |

### Budget, comparison and sources

| Piece | Layout and shared components | States to cover |
| --- | --- | --- |
| Budget | `#budget.section.wrap`; `budgetField`, `paintTotal` in `source/app.js`. `.budget-layout`, live `aside#total.budget-total`, `.budget-fields`, `.car-costs`, `.budget-actions`. | Nine regular fields and five rental fields. Default, edited valid value, zero, blank/invalid, upper bound, negative, threshold status of below/within/above, rental closed/open, stay transfer, reset, saved values on refresh. Totals are sticky in desktop and tall phone layouts. |
| Compare trips | `section#compare.wrap.comparison`; `paintCompare`, `refreshPrices` in `source/app.js`, cost chart in `source/winter.js`, `.compare-controls`, `.compare-scroll`, native table and `.compare-details`. | First and second city selects, same city in both slots, distinct names with long text, budget edits update without erasing comparison state, weather/flight/entry disclosure closed/open, target band. Inspect the inner table for scrolling separately from the document. |
| Sources | `section#evidence.wrap.evidence`; `paintEvidence` in `source/app.js`; seven native `details` for the five source lists, Photography credits and Routes, atlas and currency. | Collapsed, each open, cover/chapter credit focus and scroll, prior estimates, provenance and rights. 92 city-specific reference entries and 24 photo credits. |
| Print | Print action, `beforeprint`, `afterprint` in `source/app.js`, print CSS in both sheets. | All days temporarily open and return to prior state. Browser owns print dialog. App excludes outer chrome and photo-led sections from the printed layout. |

## Special messages, defaults and form constraints

| State or form | Labels, messages and recovery | Source |
| --- | --- | --- |
| Globe loading/capability | Loading globe. This browser is using the static atlas. The globe was interrupted. The map is still available. Asset errors and lack of WebGL return to the static map. | `source/atlas.js` |
| Briefing loading/failure | Loading visual briefing. The visual briefing could not load. The guide above is ready. A completed preview stays on the final frame. | `source/winter.js` |
| Walk data unavailable | Offline routing could not be verified for this destination. No route calculated. Time unavailable or Walk time unavailable where time is missing. These are source-defined fallback states, absent from the current 55 timed routes. Simulate them in an isolated browser context. | `paintMap` in `source/app.js` |
| Walk data valid but uncertain | Public starting point for the selected stay. District hub example with an unverified approach. City reference walk from a different starting point. No starting point was confirmed for the selected stay. Dashed guide when a public pin differs from the stored path. | `paintMap` and `source/travel-maps.json` |
| Stay or flight missing details | Price to check, Bathrooms: check listing, generic flight schedule and baggage notes. Some are defensive templates. Source notes include prices based on dated observations and real listing limits. | `stayCard`, `paintCity`, `flightLeg`, `source/travel-data.json` |
| Budget amount input | Native number field with min 0, max 150000 and step 1. JS normalizes blank or nonnumeric to 0, clamps bounds and writes back on change. No submit, Save bar, form error banner, invalid field text or custom validation notification. | `budgetField`, `n`, delegated input and change handlers in `source/app.js` |
| Budget feedback | Group total and price per adult. Below the target range, Within the preferred range, or Above the preferred budget. Includes contingency. Reset clears current city edits and stay selection and restores focus. No success toast. | `paintTotal` and Reset handler in `source/app.js` |
| Local preference unavailable | The app catches storage errors and still works within the current session. There is no message or blocking screen. An invalid initial hash uses the saved city or Baku. | `read`, `persist`, and `pageLocation` in `source/app.js` |
| Atlas, start point, walk and compare selectors | Native selects, restricted to provided values. No free-text search or validation message. Diagram/satellite and other choice buttons expose selection with `aria-pressed`. Native disclosures and photo dialog own open/closed semantics. | `source/index.template`, `source/app.js`, `source/atlas.js`, `source/winter.js` |

## Coverage counts and conventions

| City | Itinerary days | Main stays | Other stays | Walks, public starts | Winter options | Photos |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| Baku | 8 | 2 | 1 | 11, Sahil and Port Baku | 3 | 9 |
| Tbilisi | 7 | 2 | 1 | 11, Liberty Square and Station Square | 2 | 4 |
| Budapest | 8 | 2 | 1 | 11, Opera and Buda hub | 1 | 4 |
| Vienna | 8 | 2 | 3 | 11, Hauptbahnhof and VIC | 1 | 3 |
| Prague | 6 | 2 | 1 | 11, Jiřího z Poděbrad and Old Town | 1 | 4 |

The app uses the same source on both delivery forms. Start the walkthrough at 390, 1440 and 2560 CSS px. Include 320 portrait, 768 tablet and 667 landscape where breakpoints or sticky behavior change. Cover mouse, keyboard, emulated touch and reduced motion. Source-level fallbacks can use blocked optional resources or ephemeral fixture data. Document simulated states as such. Existing execution checks live in `source/verify.py`, `source/verify_premium.py`, `source/verify_winter.py` and `source/verify-independent.cjs`. The design system is the root color, type, gutter and navigation tokens and shared classes in `source/styles.css`, with additions in `source/winter.css`.

Use **Cities**, **Stays**, **Walks**, **Winter**, **Itinerary**, **Budget**, **Photos**, and **Compare** when naming areas. Keep **public starting point**, **per adult**, **for three**, **SAR**, **satellite**, and **diagram** precise. The inventory distinguishes an existing label from a potential proposal. Use regular English for new text and preserve exact place and operator names.

## Owner constraints to carry into proposals

- Keep all five cities, the December 2026 travel window, three travelers and Medina departure. Preserve comparison, sourced historical costs, booking links, realistic route and itinerary facts, licensing, accessible controls, offline parity and the paid-infrastructure-free Pages edition. [Original scope](../../GOAL.md) · [Premium decisions and tests](../../PREMIUM-EXPERIENCE.md)
- Keep the photo-led cover and city chapters, real licensed images, correct globe projections and static/reduced-motion fallback. The owner asked for a premium editorial experience rather than a generic collection of cards. This does not require lining up every photographic crop or making each practical section a full viewport. [Premium visual direction](../../PREMIUM-EXPERIENCE.md)
- Preserve real satellite and optional diagram, one selected route, scale and pins, modeled timing, named public starting point and a direct choice of Google or Apple walking directions. The owner's explicit request was “I want the path to be shown better with real satellite or terrain.” [Winter decision record](../../WINTER-FIELD-GUIDE.md)
- Keep December-specific Baku and mountain conditions and the distinction between private, shared, nearby and unconfirmed outdoor space. Unpriced alternatives do not alter the budget. The owner said “Also prefer stays with somesort of outdoor environment.” Keep the actual booking photos on original listing links when redistribution rights are unavailable. [Winter decision record](../../WINTER-FIELD-GUIDE.md)
- Maintain both actual Stageshow briefings or flag any loss as an owner conflict. Facts, links and choices are usable without playback. The owner explicitly asks to use Stageshow and Taste Skill v2 again.
- Preserve mobile budget totals, direct city access, keyboard focus restoration, and print expansion established by earlier review. Treat these as regression gates. [UI changes](../../IMPROVEMENTS.md) · [Prior releases](../../DRY-ROUND-1.md) · [Prior dry round 2](../../DRY-ROUND-2.md)
