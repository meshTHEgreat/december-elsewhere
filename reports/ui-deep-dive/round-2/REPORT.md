# Independent dry round 2 | 23 November 2026

**Pass.** This is the first clean review after the short-landscape photo fix. The review covered frozen commit `f4aff5eafc355373d187930057357e9d28bfce8d`.

| Edition | Verified SHA-256 |
| --- | --- |
| Hosted preview at `http://127.0.0.1:18768/` | `d09a0652e7e4c6c3e990420a1f8c675f32c19f29a29b0dabebdad7227f766b71` |
| Root standalone `index.html` and the browser download from the hosted preview | `93e786ba4833e97cdd9e461fe8afd485617e4d7d0f2cbcbb9c2f00651bc92340` |

Fresh Windows Chrome 157.0.8103.79 contexts exercised English left-to-right at 320 × 725, 390 × 844, 667 × 375, 768 × 1024, 1440 × 900, and 2560 × 1440. The first three used Chrome touch emulation. The standalone ran from `file://` with browser networking disabled. The review recorded zero offline HTTP requests and zero console, runtime, or HTTP errors in the monitored flows. Safari, physical touch hardware and assistive technology were outside this round.

## Short-landscape photo repair

All 24 photos in both editions displayed the entire image, complete caption, Close, Previous, Next and Download at the initial scroll position in all three phone viewports. At 667 × 375, each control measured at least 44 × 44 CSS px and passed five hit-test points. Fixed-coordinate touch input activated each control for all 24 photos per edition. All 24 browser downloads had byte-identical counterparts across the two editions. Escape returned focus to the opener in every chapter. [Hosted measurements](photos-online.json) · [Offline measurements](photos-offline.json) · [Independent touch script](review_photos.py)

| Initial photo, 667 × 375 | Close vertical bounds | Previous, Next and Download vertical bounds |
| --- | --- | --- |
| Baku Old City | 29.91–73.91 px | 301.08–345.08 px |
| Vienna Rathaus market | 19.84–63.84 px | 311.16–355.16 px |

The lowest control across the 24 views ends at y355.16, leaving 19.84 px below it. The rendered landscape viewer keeps the photo centered, attribution readable and the action row together. Vienna's three-line caption fits above the row. [Baku hosted](online-baku-667.jpg) · [Vienna hosted](online-vienna-667.jpg) · [Baku offline](offline-baku-667.jpg) · [Vienna offline](offline-vienna-667.jpg)

## Guide walkthrough

| Scope | Result |
| --- | --- |
| Five destination chapters | All six premium viewports verified 55 route selections, 10 linked stays, 24 decoded credited photos and 37 itinerary days in both editions. The map-provider URLs used audited start and end coordinates. Stay selection updated the budget, and the satellite and diagram modes preserved the selected path. [Hosted suite](premium-online.json) · [Offline suite](premium-offline.json) · [App geometry](app-online.log) |
| Navigation and atlas | The seven compact menu links fit after native toggle placement in all five cities at all phone sizes. Touch reached the globe and Vienna chapter. Keyboard moved focus to the atlas, section headings and photo opener. The globe and flat-map fallback passed, including selection continuity after WebGL context loss. [Atlas suite](atlas.log) · [Hosted walkthrough](walkthrough-online.json) · [Offline walkthrough](walkthrough-offline.json) |
| Winter | Both previews advanced through all eight scenes at 390 px. All scenes were selectable. Selecting the last scene stopped each preview while it was still playing. Reduced motion opened on Tufandag and Prague. At 667 px, Close and the whole 190 px Stage fit. Scene notes fit above progress and Escape restored focus. [Moving Baku sequence](online-stage-baku-moving-390.jpg) · [Moving five-city sequence](online-stage-overview-moving-390.jpg) · [Landscape poster](online-stage-poster-667.jpg) · [Manual interruption](manual-interruption.json) · [Hosted winter suite](winter-online.log) · [Offline winter suite](winter-offline.log) · [Stage checks](stage.log) |
| Budget, comparison and sources | All 17 edited budget controls stayed hittable when tabbed at each phone size. The stressed totals of SAR 1,400,000 and SAR 4,200,000 fit, and reset, persistence, comparison arithmetic and evidence link destinations passed. The expanded sources links met the 44 px target size. [Budget focus](budget-focus.json) · [Budget rendering](online-budget-390.jpg) · [Comparison rendering](offline-compare-390.jpg) · [Offline app suite](app-offline.log) |
| Print and offline delivery | Chrome produced the Prague A4 PDF in both editions and restored the one-open state after printing all six days. The hosted browser download matched the frozen standalone hash. [Hosted walkthrough](walkthrough-online.json) · [Offline walkthrough](walkthrough-offline.json) |
| Alignment | Each edition measured 573 states with zero document overflow, zero nested horizontal overflow and zero intended alignment spreads above 1 px. The audit recorded 750 repeated short inline credit and citation targets per edition. Larger dedicated Sources and navigation actions passed the approved target checks. [Hosted measurements](alignment-online.json) · [Offline measurements](alignment-offline.json) |

The phone cover gives the title, photographed skyline and single primary action the first screen. Stays puts the rate and outdoor-access caveat beside the listing decision. The walk picker, route summary, map and budget values retain their visual order at phone sizes. The wide arrival screen preserves the full-width header and separate reading and flight rails. [320 px cover](online-cover-320.jpg) · [390 px stays](online-stays-390.jpg) · [390 px walk](offline-walk-390.jpg) · [1440 px arrival](online-arrival-1440.jpg) · [2560 px arrival](offline-arrival-2560.jpg)
