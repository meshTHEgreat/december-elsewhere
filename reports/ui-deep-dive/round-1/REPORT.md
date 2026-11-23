# Independent dry round 1 | 23 November 2026

**Failed.** The Previous and Next controls in the landscape photo viewer are clipped on initial display in 19 of 24 photo states in both editions. The candidate does not advance the consecutive release count.

| Candidate | SHA-256 |
| --- | --- |
| Hosted preview at `http://127.0.0.1:18768/` | `6531786a1a2e8c365cbfd3ff055f440cd3bfc04c9191b94ebbfe4cc40d85d48b` |
| Standalone `index.html` and hosted `offline.html` download | `50ad87e74d97e873a66148c251cbcc2ce58ea7d0ee289d9328425efcb5411ff8` |

Artifact commit `c84bbf9`. The premium suite used test-only commit `54efbea`, which updated an assertion to read the expected route name from the audited dataset after route buttons moved into a collapsed disclosure. The HTML hashes stayed the same. The hosted download was exercised as an actual browser download and verified against the standalone hash.

## Release blocker

Open Vienna → Photos and tap the first photo in a fresh 667 × 375 browser context. The viewer opens at scroll position 0. The Previous and Next rows start at y358.56 and end at y402.56, leaving only 16.44 of the 44 px targets visible. Their labels sit below the screen, and a hit test at the Next button center fails. The same occurs in Prague's second photo. The other 17 affected photo states leave 36.58 of 44 px visible. The caption, image, download and Close are visible. Arrow-key cycling works, and the buttons work after scrolling. The viewer has 40 px of internal scrolling on Vienna's first photo.

| Chapter | Clipped photo states |
| --- | --- |
| Baku | 8 of 9 |
| Tbilisi | 4 of 4 |
| Budapest | 3 of 4 |
| Vienna | 2 of 3 |
| Prague | 2 of 4 |

All 24 states fit at 320 × 725 and 390 × 844. A landscape fix should retain the full image aspect ratio and keep Close, the complete caption, Download, and the full Previous and Next hit areas in the initial viewport. The checks should include every photo and the longest attribution. [Offline screenshot](clip-vienna-offline.jpg) · [Online screenshot](clip-vienna-online.jpg) · [Prague second photo](mobile-online/667/photo-prague-2.jpg) · [Reproduction measurements](photo-clip-reproduction.json) · [Reproduction script](reproduce_photo_clip.py)

## Checks completed

Fresh Windows Chrome 157.0.8103.79 used isolated contexts at 320 × 725, 390 × 844 and 667 × 375 first, followed by 768 × 1024, 1440 × 900 and 2560 × 1440. The standalone opened from `file://` with browser networking disabled. Every main and supplemental offline run recorded zero HTTP(S) requests. The hosted flows fetched media from the preview origin. No physical phone, Safari or assistive technology was used in this round.

| Scope | Result |
| --- | --- |
| Five chapters and content | Each premium context exercised five chapters, ten stays, 37 itinerary days, 24 credited and decoded photos and 55 paths. Direct placement, listing URLs, trip assumptions, day disclosures and the stay-to-budget handoff passed. |
| Navigation and atlas | Touch and keyboard opened chapters and section links. The compact menu fit for all five chapters at all three phone dimensions after native toggle placement. The globe, city selection, chapter focus and flat-map fallback passed. |
| Walks and geography | All 55 route selections used the audited endpoints in Google and Apple links. All five city mosaics and both anchor states were sampled in the satellite layout. Switching the diagram and satellite backgrounds preserved the route. The short-landscape route check kept at least 90% of the map and the full trace visible. |
| Winter previews | Both real sequences played at 390 px. Manual scene selection and reduced-motion posters were exercised. All eight scenes were selected and inspected for note-to-track fit. At 667 × 375, both scenes initially fit from y174.02 to y364.02, and focus reached Close. Escape returned focus to the trigger. |
| Budget, compare and sources | At each mobile dimension, 17 focused budget controls remained hittable after editing. Maximum exercised totals read SAR 1,400,000 and SAR 4,200,000. Reset, reload persistence, comparison arithmetic, no table overflow and published evidence action targets passed. |
| Print | Chrome produced an A4 document from the Prague chapter in all phone contexts. Print expanded six days and restored the prior one-open state afterward. |
| Alignment and targets | The fresh shared measurement captured 573 states per edition with no document overflow, no nested horizontal scroll and no flagged intended spread above 1 px. The target audit flagged 750 repeated inline citation/attribution occurrences per edition below 44 px. Approved navigation and expanded Sources targets passed their targeted checks. |

[Hosted premium matrix](premium-rehearsal-online.json) · [Offline premium matrix](premium-rehearsal-offline.json) · [Hosted winter suite](winter-online.log) · [Offline winter suite](winter-offline.log) · [Hosted app checks](verify_ui_app.py-online.log) · [Offline app checks](verify_ui_app.py-offline.log) · [Atlas checks](verify_ui_atlas.py-online.log) · [Stage checks](verify_ui_stage.py-online.log)

[Hosted alignment](alignment-online.json) · [Offline alignment](alignment-offline.json) · [Hosted phone walkthrough](mobile-online.json) · [Offline phone walkthrough](mobile-offline.json) · [Settled menu recheck](menu-settled-reproduction.json) · [Offline 320 contact sheet](contact-offline-320.jpg) · [Hosted 390 contact sheet](contact-online-390.jpg) · [Landscape preview scene](mobile-offline/667/stage-overview-5.jpg)

The first supplemental menu measurements could run before the browser dispatched the deferred native `toggle` event, and those observations remain in the raw files. A separate settled recheck across 30 states measured each menu after two animation frames and passed. The photo measurements followed image decoding and reproduced from a separate fresh Chrome run bound to the candidate hashes.
