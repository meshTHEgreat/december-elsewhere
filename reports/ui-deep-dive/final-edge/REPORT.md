# December, Elsewhere · Final Edge review

**Pass.** Reviewed source `b1eae0834ab08f52d863d95e0ac104d9986e43d0` on Microsoft Edge 158.0.4370.33 for Windows on 23 November 2026. Fresh English LTR contexts covered 320 × 725, 390 × 844, 667 × 375, 768 × 1024, 1440 × 900, and 2560 × 1440. The three smallest viewports used emulated touch. The wider viewports used keyboard input.

| Edition | Tested artifact | SHA-256 |
| --- | --- | --- |
| Web | `http://127.0.0.1:18771/december-elsewhere/` | `cc8cdb7db4b3e055b16aff121cc69b09838be0ae8b57cb4d25fa40c5e131177c` |
| Offline | `december-guided/index.html` with networking disabled. The preview’s `offline.html` download matched these bytes. | `97fb156c67024730f0894985a7a27dcf2351d46245720b4e84fec26c4539fe2b` |

## Local guides

- Opened each chapter’s direct guide link, activated both choices, and checked the journey stops, recommendation, caveat, and all 31 rendered source-link placements at every tested width in both editions. Only one choice opened at a time. All measured guide controls were at least 44 × 44 CSS px and the longest full line was 73 characters. [Web suite](guided-web.log) · [Offline suite](guided-offline.log) · [Baku day trip](web-baku-day-390.png) · [Tbilisi overnight](offline-tbilisi-night-390.png)
- The Baku day-trip link matches GetYourGuide product `t517765`. The guide copy flags that prices and availability for the trip dates are unconfirmed, calls out road or seasonal constraints where applicable, and prompts travelers to verify what the guide and quoted price cover. I verified the displayed destinations and link attributes. Supplier inventory and booking were outside this UI check. [Exact product link](https://www.getyourguide.com/baku-l1408/baku-gobustan-mud-volcano-fire-mount-temple-lunch-entry-t517765/)
- Opening or switching choices preserved all 37 itinerary day panels, their open states and contents, the budget fields and total, and the comparison. Update the budget moved focus to the Budget heading and set the correct chapter hash. [Interaction record](interactions.json)

## Regression checks

| Check | Result |
| --- | --- |
| Full geometry | 663 measured states per edition, including 90 guide states. No document or measured regional horizontal overflow and no measured alignment spread. [Summary](geometry-summary.json) · [Web measurements](geometry-web.json.gz) · [Offline measurements](geometry-offline.json.gz) |
| Planning | The default premium suite passed in both editions. It covered all five chapters, 10 stay selections, 37 itinerary days, 55 walking paths and provider links, 24 photos, budget and comparison persistence, A4 print lifecycle, and the real Globe and static fallback. [Web](premium-web.log) · [Offline](premium-offline.log) |
| Winter | The default winter suite passed in both editions, including the satellite and diagram controls and both previews with motion and reduced motion. [Web](winter-web.log) · [Offline](winter-offline.log) |
| 667 × 375 Stage | With either motion preference, tapping a preview and its first scene followed by native Shift+Tab focused the fully visible 116.55 × 44 px Close button. The full 460 × 190 px stage and every named scene button remained in view. Close and all scene centers passed hit testing. Closing restored trigger focus. A simulated partial mount failure showed the fallback message and kept the panel hidden. [Web overview](web-667-overview-focus.png) · [Offline regional](offline-667-baku-focus.png) |
| 667 × 375 photos | Every photo decoded in both editions. For each of the 24 states per edition, Close, Previous, Next, and Download were fully in view and passed center hit testing. Escape returned focus to the thumbnail. [Web](photos-web.log) · [Offline](photos-offline.log) · [Photo capture](offline-667-photo.png) |

The recorded runtime checks had zero browser or resource errors. The offline checks recorded zero HTTP requests. Inline provider and photo-credit links outside the new guide section retain the earlier sub-44 px measurements.
