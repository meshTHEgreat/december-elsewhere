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
