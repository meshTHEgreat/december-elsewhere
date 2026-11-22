# Independent offline review

**Reviewer:** A separate review pass from the application implementation. Focus on package integrity, travel claims and provenance, functional behavior, privacy, and photo accuracy.

**Disposition:** A fresh JavaScript contract run passed. A browser end-to-end pass was blocked, so this report alone does not qualify as a successful dry round.

## Executed checks

- Loaded the packaged `index.html` directly, parsed the embedded dataset and ran the same application JavaScript in a fresh Node VM with simulated document and storage. The harness provided no network API. Checked inline content-security policy, CSS dependencies and externally loaded tags.
- Exercised all five destination selections, both recommended properties per destination, the five day lists, neighborhood anchor controls and route highlighting controls, all 11 gallery images, budget changes and comparison selection. Changing a per-person expense by SAR 101 moved the group total by SAR 303. A SAR 300 group rental moved it by SAR 300. Property changes adopted the listed price. Restarted with saved state and with storage access denied to test both paths.
- Verified embedded photo bytes against the originals in the portable folder. Confirmed all 11 WebPs decoded via Pillow, dimensions matched the manifest, and every gallery slide displayed the corresponding credit and license URL. The manifest identifies archive photography.
- Parsed 235 unique research and image links across 46 hosts. Syntax validation alone is distinct from online retrieval. Opened all ten exact Airbnb URLs independently. Seven returned the expected listing title. The revised bundle also passed geometry sanity checks across 55 pedestrian paths. The worst endpoint snap was 73 m. The benchmark checks alignment, source labeling, and reported distance/duration arithmetic. It does not reproduce the routing engine’s trip calculations.
- Attempted a fresh local Playwright/Chromium run in offline mode. The executable exited before navigation with `ProcessSingleton: socket() failed: Operation not permitted`. This environment could not provide Chromium screenshots, touch, visual layout, native details rendering, or console measurements.

To reproduce the JavaScript checks from the portable folder, run `node reports/independent-runtime.cjs .`. Its output records the tested file hash and counts.

## Findings

| Severity | Finding and evidence | Proposed resolution or limitation |
| --- | --- | --- |
| High | The first integrated application snapshot had 55 coordinate pairs and zero retrieved pedestrian paths or walking times. The initial UI inserted blank minute and kilometre units and called the panel pedestrian paths. | Resolved and retested in the Node VM. The revised artifact includes 55 Valhalla/OSM geometry traces and 55 modeled walking durations. It identifies the public anchors and distinguishes estimated or unavailable paths when relevant. |
| High | Exact property photos could be located at original listing pages but redistribution permission was not established. The offline application is limited to genuine destination photographs and listing-gallery links. | Retain listing links and explain the constraint. Repackage only after a rights holder supplies permission or independently licensed exact-listing imagery can be substantiated. [Airbnb platform terms](https://www.airbnb.com/help/article/2908). |
| High | The required two consecutive clean browser dry rounds cannot be credited from simulated JavaScript checks. The local browser blocked before navigation. | Use independent real-browser environments for full dry rounds. Record blocked features separately. |
| Medium | Link retrieval for Vienna listings 1644751971236465063 and 47782977, and Prague listing 1566707663347121616, failed during independent external checks. The failures establish retrieval uncertainty. | Preserve original evidence and suggest a retrievable fallback with its own ID and separately qualified price. [Vienna Airbnb fallback with two bedrooms and three beds](https://www.airbnb.com/rooms/13454321). [Prague Booking.com fallback](https://www.booking.com/hotel/cz/cozy-home-2.html). |
| Medium | On the initial UI, collected apartment-access and Booking/aparthotel observations were omitted from rendering, and the mobile flex strip put later destinations beyond the initial view. | Retest confirmed Booking/aparthotel alternatives rendered in the updated application source. Mobile discoverability still needs visual testing. |
| Low | Photo re-encoding was fully documented in manifests, with attribution and license links in the standalone page. The standalone page should also disclose WebP conversion. | Show modification notes beside photo attribution in the evidence section. |

Booking-platform listing pages and source links remain intentionally online. Their existence provides no evidence of date-specific availability, final fees, or exact walking distance from a private entrance.
