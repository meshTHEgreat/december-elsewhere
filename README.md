# December, elsewhere

Open [the online guide](https://meshthegreat.github.io/december-elsewhere/) or download the [self-contained offline edition](https://meshthegreat.github.io/december-elsewhere/offline.html). Open the offline file in a current browser. Photography, the atlas, route diagrams, day plans, the budget calculator and comparisons are embedded. Browser-local storage can remember choices and budget changes when the browser permits it. Booking, source and external directions links require internet.

## Start here

- The atlas previews direct distances from Medina airport to the five city centers. Choose a city in the atlas selector or opt into the interactive globe. Each chapter shows its published flight routing and layovers.
- Pick a destination, then choose an apartment. The stay price updates in the budget and its public neighborhood anchor appears on the map when matched.
- Choose any walk to highlight the pedestrian route. The starting point is a public landmark, square or station. Two properties could not be linked to a reliable public starting point.
- The walk map offers a real Sentinel-2 satellite view and a diagram. Google Maps and Apple Maps open walking directions using the same two public points.
- Winter covers the trip dates, outdoor activities, direct operator links, and two optional Stageshow presentations. Stay cards distinguish private outdoor space, nearby public space, listed amenities with unclear access, and unverified claims.
- Change meals, fares and other costs to compare the group's options. Open Car rental costs when needed. Driver, lodging and car inputs are shared. All remaining inputs are per adult. A rental should replace the driver line when the two cover the same outing.
- Open the original accommodation page for the actual room photos and to confirm availability, fees, bedding and arrival arrangements. All 24 licensed place photographs can be viewed and downloaded from the guide.
- Print from a destination's budget area to expand the full itinerary for printing.

## Source and maintenance

| Path | Contents |
| --- | --- |
| `index.html` | Standalone deliverable. The identical downloadable copy is `docs/offline.html`. |
| `docs/` | GitHub Pages root, with local photos, type and on-demand globe media |
| `source/index.template`, `source/styles.css`, `source/app.js` | Static application |
| `source/travel-data.json` | Dated research, prior estimates, operating assumptions and alternatives |
| `source/travel-maps.json` | 55 pedestrian routes from 10 public anchors, including modeling caveats |
| `source/photography.json`, `assets/PHOTOGRAPHY.md` | Photograph sources, licenses and modifications |
| `reports/` | Goal, improvement log, independent findings, route audit and verification status |

Run `python3 source/build.py` to regenerate both formats. Python’s standard library is sufficient. Serve `docs/` for the online build. The atlas uses [public-domain Natural Earth land geometry](https://www.naturalearthdata.com/about/terms-of-use/). Walking map data © OpenStreetMap contributors, [ODbL 1.0](https://www.openstreetmap.org/copyright). Routes were calculated using the [Valhalla service](https://valhalla1.openstreetmap.de/). Photographs carry their individually indicated licenses. Three.js and the locally packaged fonts carry their MIT and SIL Open Font License notices in `source/vendor/` and inside the offline edition.

Run `python source/verify_premium.py` with Python Playwright and Chrome or Edge to test the offline file. Pass a Pages or subpath-preview URL to run the same interactions against the hosted edition. The [premium review log](reports/PREMIUM-EXPERIENCE.md) records design decisions and review evidence.

Two independent package/runtime checks are reproducible with `node source/verify-independent.cjs reports/independent-package-audit.json` and `node reports/independent-runtime.cjs . > reports/independent-runtime.json`. The browser regression script is `python3 source/verify.py browser-results.json` with Playwright and its Chromium installed. See the verification report for checks actually executed.

Run `python source/verify_winter.py` for the winter guide, Stageshow and satellite regressions. See [the winter release record](reports/WINTER-FIELD-GUIDE.md) for operator sources and rehearsal evidence. The standard-library Python build uses locally vendored Stageshow and React assets. `source/prepare-winter-stage.mjs` can regenerate the vendored scene from the installed skill. `source/fetch-walk-basemaps.py` refreshes the open Sentinel-2 imagery when needed.
