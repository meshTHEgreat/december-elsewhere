# December, Elsewhere premium experience

**Goal.** Transform the existing travel planner into a premium, immersive, geographically realistic, mobile-first travel discovery experience with reliable offline and GitHub Pages delivery.

**Baseline.** Commit `94720b4`. The live release and its offline artifact retain five cities, 55 routed walks, ten primary stays, and 37 itinerary days. The opening and chapter headers repeat the same photographic treatment. Galleries sit after the budget, route geometry feels disconnected from the stay decision, and itinerary disclosures give each day the same visual weight. The trip comparison is legible but dense. Preserve the evidence, responsive interactions, keyboard focus, and calculator logic as the composition changes.

## Acceptance

- Five materially distinct city chapters with a coherent visual language, a usable first screen, and readily discoverable jumps. Show the December 2026 dates, Medina departure, and three-traveler assumptions.
- Authentic photos with readable crops and complete credits. Label neighborhood and property imagery accurately. Keep the original listing galleries available through direct links.
- A real-coordinate geographical moment that explains the trip. Keep the content operable with WebGL unavailable or motion reduced. Preserve the 55 walking paths and the distinction between public anchors and apartment pins.
- Preserve budget arithmetic, comparison, stays, routes, all itinerary stops, source links, keyboard navigation, print, and compatibility with saved preferences.
- Generate Pages and offline editions from the same application and research. The downloadable HTML must match the root standalone byte for byte. Verify narrow phones, landscape, tablet, desktop, and fresh offline browsers. Capture motion frames and keep measured evidence.
- Two separate independent end-to-end rounds on the same release. Record the commit, bundle hash, browser and device conditions, actual results, source and geographic checks, and reviewers’ findings. Reset the count for material defects. A blocked check is inconclusive.

## Ranked backlog

| Rank | Change | Visual impact | User value | Complexity | Regression risk |
| --- | --- | --- | --- | --- | --- |
| 1 | Photographic cover, editorial typography, and unmistakable city discovery | High | High | Medium | Low |
| 2 | Distinct chapters, section navigation, photography inside the journey, and an actionable ending | High | High | Medium | Medium |
| 3 | Stay-to-walk handoff and a readable map with a revealed verified path | High | High | Medium | High |
| 4 | Offline geographical atlas with a locally bundled Three.js view and visible static map | High | Medium | High | Medium |
| 5 | Itinerary pacing, full-screen gallery, and decision-focused budget comparison | High | High | Medium | Medium |
| 6 | Additional researched imagery, interaction filming, performance, accessibility, and independent dry rounds | High | High | High | Medium |

## Art direction

An atlased winter travel publication. Warm paper, deep olive-black ink, tarnished gold route lines, and saturated photography. Headlines read like a print cover. Wayfinding uses a quiet sans serif with consistent typographic hierarchy. The chapter compositions alternate image, breathing room, and practical detail. Motion focuses attention on a selected route, a selected city, and the progression through a chapter.

Taste v2 design settings for exploration are variance 7, motion 5, density 3. Planning tools retain denser, aligned text. The current Taste skill informs photographic composition, repeatable gutters, readable stills, touch sizing, and browser inspection. Stageshow informs retained framing, ordered dependent changes, inspecting the onset and hold, and recording narrow and wide views. This is an existing travel application with licensed captions and an explicit geographic WebGL brief, so those requirements guide exceptions to the marketing-page templates.

## Review state

The release candidate is commit `228eba3`. The final online and offline HTML use the same city, stay, route, itinerary, and photographic data. The Pages version fetches same-origin media on demand. The 6.6 MB standalone includes all photos, atlasing code, land geometry, fonts, and license notices.

| Edition | SHA-256 |
| --- | --- |
| Offline | `e6df97ff7b1a1e404a9a44e6e5fb31015221968ec7185eac5e7f3b284555ae40` |
| Pages | `33b23d096227cb0d81d10faf76754a0d020488784b027069456d5ec4b6a61bba` |

## Design and geography

- A Prague winter cover sets the visual language. Each destination has its own photographic introduction, locally bundled Bodoni Moda and Manrope, flight legs, stay selection, a route-led neighborhood section, an itinerary, the budget, a full-screen photo journal, and a short decision prompt. The chapter menu and direct section links support skipping.
- Flat atlas, globe, and scroll-driven photography were rendered in the browser. The flat atlas is the quickest way to read labels and compare destinations. The 3D globe adds scale and geographic orientation on demand. The walking maps keep their audited SVG geometry and use drawing motion to reveal the selected path. The photographic story uses the actual photos at varied crops and scales.
- Direct-distance figures use great-circle distance from Medina airport to representative city centers. Actual flights and layovers appear in the chapter. The local routes start at named public places. Vienna and Prague listings without verified linked route anchors retain clearly identified city examples. District hub distances start at the hub. [Natural Earth](https://www.naturalearthdata.com/about/terms-of-use/) · [MED location](https://ourairports.com/airports/OEMA/) · [Walk dataset](../source/travel-maps.json)
- Six licensed photographs were added. Gallery captions and Sources carry dates where known, creator, license, and modifications. Property galleries open the booking listing so readers can see the actual apartments. [Photography credits](../assets/PHOTOGRAPHY.md)

## Improvement cycles

| Cycle | Evidence and changes |
| --- | --- |
| Baseline audit | Separate creative, browser performance, and travel-access reviewers identified the weak seasonal opening, repetitive chapter cadence, hidden galleries, location ambiguity, mobile wayfinding, and monolithic transfer. The original guide was preserved as the comparison. |
| First render | The independent creative reviewer flagged the clipped phone menu, hard city jump, repeated cover image, hidden mobile walk trace, and tall landscape opening. The technical reviewer filmed an incorrect antimeridian band and measured the initial mobile guide at about 22 seconds with all enlarged media in one response. The travel reviewer identified exact listings and dated transfer corrections. |
| Refined candidate | Changed the compact menu direction and landscape grid, moved the mobile route chooser above the map, drew the selected walk in view, clarified city preview versus chapter selection, differentiated the Prague and Tbilisi chapter images, and put duration and both prices on each chapter cover. Kept focus on the globe toggle during loading and made the entire atlas panel visible on activation. |
| Release checks | Corrected coastline seam wrapping, verified GPU disposal and disabled-WebGL fallback, split the online media, and used embedded photographic previews while full images decode. Confirmed the Vienna rail closure and current public listing details. Preserved old prices as dated observations. Checked narrow reflow and keyboard reach, including the lightbox and calculator. |

### Measured performance

Three cold runs per version, Chrome 157 at 390 × 844 CSS px, 3× DPR, 4× CPU throttle, 1.6 Mbps downstream and 150 ms latency. The original Pages payload and compact preview were served by the same gzip harness. The measured compact snapshot was `fdec734`.

| Median | Original payload | Compact preview |
| --- | ---: | ---: |
| Destination controls usable | 14.94 s | 1.67 s |
| Largest Contentful Paint | 15.52 s | 1.93 s |
| City selection to two animation frames | 107 ms | 78 ms |
| Cumulative layout shift | 0.124 | 0.0036 |

Globe loading waits for an explicit request. The module retains a single scene, caps device pixel ratio at 1.5, stops rendering at rest, and disposes the scene on chapter navigation or when the atlas leaves view. Local software and real device performance can vary.

The published release was measured separately with the same mobile emulation and throttle. Across three normal-motion runs, median LCP was 2.25 seconds and the city controls were ready in 1.84 seconds. Three reduced-motion runs yielded 2.14 and 1.85 seconds. Normal and reduced motion drew the optional globe in a median 2.28 and 1.59 seconds after activation. One live normal-motion run reached 4.42 seconds LCP. [Live benchmark](premium-evidence/live-render-perf.json) · [Offline benchmark](premium-evidence/offline-render-perf.json)

### Rehearsal and compatibility

Taste’s browser inspector covered desktop, tablet and 320/390 px layouts. It reported template-specific height, neighbor and asymmetric gutter rules for this long editorial. The assessment kept content-sized sections and the deliberately asymmetric grid. Its detector also treated the visible sticky header as a missing nav height. Direct browser inspection, focus tests, and overflow checks covered those geometries.

Stageshow’s retained-frame choreography informed the chapter entrance, route stroke, and globe turn. Browser recordings document normal playback. Route frames at 0, 80, 160, 320, 520, and 780 milliseconds show the actual path and the settled state. The reduced-motion mode retains the same content and controls.

| Evidence | Desktop | Mobile portrait |
| --- | --- | --- |
| Before and after | [Cover comparison](premium-evidence/before-after-1440.jpg) | [Cover comparison](premium-evidence/before-after-390.jpg) |
| After screenshots | [Cover, atlas and all chapters](premium-evidence/chapter-contact-1440.jpg) | [Cover, atlas and all chapters](premium-evidence/chapter-contact-390.jpg) |
| Motion recording | [Atlas and walk video](premium-evidence/atlas-and-walk-1440.webm) | [Atlas and walk video](premium-evidence/atlas-and-walk-390.webm) |
| Intermediate frames | [Route frames](premium-evidence/route-motion-1440.jpg) | [Route frames](premium-evidence/route-motion-390.jpg) |

Five-city core smoke checks passed in Firefox 140 and WebKit 26 at 390 px on the Pages preview. Both ran the offline file as well. Windows WebKit’s offline context flag prevented local navigation, so the local WebKit check used request interception to block HTTP(S). The formal fresh offline rounds use browser-level offline mode in Chrome and Edge. Results use emulated phone and tablet hardware.

## Release decision

Both consecutive independent dry rounds passed against the frozen release hashes. Round 1 combined the creative reviewer’s Chrome test and the engineering reviewer’s live asset, benchmark, and GPU checks. Round 2 was a separate Edge run led by the travel and accessibility reviewer. The application bytes from the reviewed build are published at the existing GitHub Pages URL.

- [Dry round 1](DRY-ROUND-1.md)
- [Dry round 2](DRY-ROUND-2.md)

Ten primary listing links returned their public listing pages. Some airline, schedule, and alternate accommodation sites blocked automated checks. The app retains dated research and service links for a human booking check. Photos are authentic place and neighborhood imagery. The property links carry the source accommodation galleries.
