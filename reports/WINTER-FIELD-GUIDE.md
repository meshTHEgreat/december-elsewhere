# Winter field guide release goal

Extend December, Elsewhere with useful visual presentations, directly viewable and downloadable licensed photography, and date-aware winter choices around Baku and across the five destinations. Preserve the decision tools and the two delivery formats.

## Acceptance

- Let a traveler find Winter from every city and jump between photographs, activity information, and official links. Inspect narrow portrait, short landscape, and wide desktop at the actual deployed URL.
- Show Baku’s coastal winter separately from Shahdag near Qusar and Tufandag near Gabala. Show which activities depend on snow, wind, road conditions, or the resort’s operating schedule. Distinguish the 5–12 December 2026 trip from historical photographs and opening patterns.
- Show how the other destinations fit their own dates. Cite tourism boards, event calendars, resort operators, and route sources. Treat external status, passes, and transport quotations as variable.
- Ship and film two optional on-site presentations built with the real Stageshow Stage runtime. Provide the practical planning information as ordinary HTML and honor reduced motion.
- Add maps and price marks that answer actual trip questions. Preserve all 55 audited pedestrian routes, 37 itinerary days, budget arithmetic, and saved preferences.
- Show the chosen walk on a correctly aligned local satellite basemap. Keep a diagram alternative and put Google Maps and Apple Maps walking directions one click away.
- Surface private, shared, nearby, and unconfirmed outdoor space where the original listing supports the distinction. Keep unpriced alternatives separate from the live budget.
- Bundle credited, licensed photographs that visitors can view and download offline. Describe weather and season accurately. Retain booking links for the actual rooms.
- Build and test on a safe branch, inspect film frames and basic layout, and verify both final artifacts on GitHub Pages before closing the goal.

## Decisions and improvements

| Priority | Initial finding | Change | Impact and regression risk |
| --- | --- | --- | --- |
| 1 | Selected Walk showed a schematic of several competing paths. | Project the selected path over one locally bundled true-color satellite scene per city. Zoom around the chosen walk and show endpoints, an orientation and scale aid, and the distinction between a public pin and a snapped routing endpoint. Offer the original diagram background and direct walking navigation. | High impact for every walk. Overlay extents and all 55 provider destination pairs are browser-tested. |
| 2 | Trip planning had seasonal mentions without a clear decision for mountain activities during Baku’s actual dates. | Add date-specific winter sections, a weather-dependent Shahdag or Tufandag day, and official checks for access, snow and lift operation. | High planning value. Existing budget inputs, itinerary days and traveler assumptions remain the source of record. |
| 3 | Outdoor access and place photography were hard to compare. | Describe outdoor access in both the stay cards and comparison table. Add linked alternatives and seven licensed photographs, with a full-screen view, download and credits. | High value with little app risk. Apartment photography remains accessible via the original listing galleries. |
| 4 | The previous release borrowed Stageshow’s choreography workflow. | Build actual Stageshow Stage sequences using the winter field guide’s image and note data. Reserve the motion for opt-in briefings, with a static frame for reduced-motion visitors. | Moderate design impact. The separate runtime loads on demand and all planning information stays accessible in the chapter. |
| 5 | The first implementation framed all routes together and used desktop composition on the phone stage. | Refocus the map on one trace with an immediate, readable line. Stack photographs above the text in the compact stage and keep the details and progress bar within its frame. | High improvement on narrow screens. Checked at 320 and 390 pixels, short landscape, and desktop. |

## Sources and limits

- Baku’s trip is 5–12 December 2026. Shahdag winter sports displayed “Opening soon” during the source check. Use the live report for snow and lift openings and check the sightseeing lift and piste information independently at Tufandag. [Shahdag live report](https://shahdag.az/en/live-info) · [Shahdag activities](https://www.shahdag.az/en/sports-activities) · [Tufandag lifts and slopes](https://www.tufandag.com/en/lifts-slopes)
- The photographs have individual author and license credits and capture dates where available. Listing rates and private outdoor access outside the disclosed listings require direct confirmation. [Photography register](../assets/PHOTOGRAPHY.md) · [Outdoor listing references](../source/outdoor-stays.json)
- The bundled scenes are September 2025 archival satellite imagery from Copernicus Sentinel-2. Their source resolution is about 10 m for visible bands. The route is selected and projected independently of the imagery. The site links to the original scene and both map providers. [Scene catalog](../source/walk-basemaps.json) · [Copernicus data terms](https://dataspace.copernicus.eu/terms-and-conditions) · [Google Maps URL format](https://developers.google.com/maps/documentation/urls/get-started) · [Apple Maps URL format](https://developer.apple.com/documentation/mapkit/unified-map-urls)

## Render and motion evidence

- Compared the same 10-minute Port Baku walk in the old deployed guide and the new build. The default keeps other walks in the chooser and frames the one selected route. [Phone comparison](winter-evidence/selected-walk-before-after-390.jpg) · [Desktop comparison](winter-evidence/selected-walk-before-after-1440.jpg)
- Filmed the interactively opened briefings at 390 and 1440 pixels. Inspected compositions before, during and after each change of beat using the Stageshow framing sheets. The short text fade follows the start of the photo crossfade. The progress mark advances with the facts, and the last scene holds. [Baku recording](winter-evidence/briefing-baku-390.webm) · [Five-city recording](winter-evidence/briefing-overview-1440.webm) · [Phone frames](winter-evidence/rehearsal-baku-phone.jpg) · [Desktop frames](winter-evidence/rehearsal-five-desktop.jpg)
- The Stageshow gate reported no layout findings in its samples. Its motion coverage was inconclusive because the sampler exceeded its 11 ms gap limit in both sequences. The browser independently reached the final frame in normal motion and the static poster in reduced motion. [Phone rehearsal log](winter-evidence/rehearsal-baku-phone.json) · [Desktop rehearsal log](winter-evidence/rehearsal-five-desktop.json)
- Taste Skill’s browser inspector reported no horizontal overflow at 390, 768, 1024 and 1440 pixels. Its whole-screen section and grid heuristics flagged the site’s custom mast, the short evidence section and several column edges, including the intentional photo and copy split in Winter. Those flags were reviewed visually. The browser layout tests checked the new interactions directly. [Taste layout output](winter-evidence/taste-layout.json)

## Release verification

- GitHub Pages built commit `10ea858` from `main:/docs`. The downloaded live HTML matched the repository build byte for byte in both delivery formats. [Pages deployment](https://github.com/meshTHEgreat/december-elsewhere/actions/runs/45084000434)
- The standalone SHA-256 is `6f908f1da7caf08885a418da6b666781f29f8d27135547e59dadf2025a29476e`. The hosted index SHA-256 is `d61fa7bd01cb8f8d38f16d6d5915a651f2564f3474a873fe28e9d1f46298a79f`.
- The standalone Chrome tests used fresh browser contexts and disabled networking. All five satellite scenes and both briefings passed at 320, 390, 667 and 1440 pixels with zero HTTP requests and zero errors. The core regression also checked storage, city navigation, walking, stays and budget behavior at 390, 768 and 1440 pixels. [Winter offline test](winter-evidence/offline-release.json) · [Core offline test](winter-evidence/core-offline.json)
- At the published URL, Chrome passed all 55 walks and both sets of directions parameters, 24 photographs, 37 itinerary days, ten stay changes, budget, print, the interactive globe and the static atlas fallback. Edge passed the winter flows, satellite views, photo downloads, and presentations at four sizes with zero browser errors. [Live Chrome regression](winter-evidence/live-premium.json) · [Live Edge verification](winter-evidence/live.json)
- The initial live page transferred about 351 kB in the unthrottled Chrome runs. LCP was 436–524 ms and CLS was 0–0.011. The Stage and globe were deferred. The Baku satellite image was 28 kB and the briefing runtime transferred 62 kB when opened. These are lab observations from one run per viewport. [Live performance data](winter-evidence/live-performance.json)
- Phone and tablet checks used browser emulation. This follow-on update has targeted verification evidence. The two independent dry rounds in this repository document the earlier premium release.
