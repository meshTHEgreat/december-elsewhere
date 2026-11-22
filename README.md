# December, elsewhere

Open `index.html` in Chrome, Edge, Firefox or Safari. The same HTML is provided as the separate direct download. The image galleries, route diagrams, day plans, budget calculator and comparison are embedded. Browser-local storage can remember choices and budget changes on browsers that allow it for local files. Booking, source and external directions links require internet.

## Start here

- Pick a destination, then choose an apartment. The stay price updates in the budget and its public neighborhood anchor appears on the map when matched.
- Choose any walk to highlight the pedestrian route. The starting point is a public landmark, square or station. Two properties could not be linked to a reliable public starting point.
- Change meals, fares and other costs to compare the group's options. Open Car rental costs when needed. Driver, lodging and car inputs are shared. All remaining inputs are per adult. A rental should replace the driver line when the two cover the same outing.
- Open the original accommodation page to see the property's photos and recheck availability, total fees, bedding and arrival arrangements. The eleven bundled photographs show the destinations.
- Print from a destination's budget area to expand the full itinerary for printing.

## Source and maintenance

| Path | Contents |
| --- | --- |
| `index.html` | Standalone deliverable |
| `source/index.template`, `source/styles.css`, `source/app.js` | Static application |
| `source/travel-data.json` | Dated research, prior estimates, operating assumptions and alternatives |
| `source/travel-maps.json` | 55 pedestrian routes from 10 public anchors, including modeling caveats |
| `source/photography.json`, `assets/PHOTOGRAPHY.md` | Photograph sources, licenses and modifications |
| `reports/` | Goal, improvement log, independent findings, route audit and verification status |

Run `python3 source/build.py` to regenerate the single file. Python's standard library is sufficient. For a private static deployment the generated index can be served unchanged. Map data © OpenStreetMap contributors, [ODbL 1.0](https://www.openstreetmap.org/copyright). Routes were calculated using the [Valhalla service](https://valhalla1.openstreetmap.de/). Photographs carry their individually indicated licenses.

Two independent package/runtime checks are reproducible with `node source/verify-independent.cjs reports/independent-package-audit.json` and `node reports/independent-runtime.cjs . > reports/independent-runtime.json`. The browser regression script is `python3 source/verify.py browser-results.json` with Playwright and its Chromium installed. See the verification report for checks actually executed.
