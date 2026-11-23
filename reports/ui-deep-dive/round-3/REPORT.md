# Dry review 3 - fail

Candidate `f4aff5e` has a reproducible keyboard focus obstruction in both Stageshow previews at 667 × 375. The same obstruction occurs on the hosted preview and in the network-disabled standalone. The landscape photo correction passes. This review breaks the consecutive clean count.

## Release blocker

1. At 667 × 375, open either winter preview by touch. Close preview receives focus and is initially clear of the sticky chapter navigation.
2. Press Tab to focus the first scene, Enter to select it, and Shift+Tab to return to Close preview.
3. The browser reports Close preview as focused and matches `:focus-visible`. The button spans y79.02–123.02, while navigation covers the page through y103.59. The sticky navigation covers 24.58 px of the 44 px button, including its center and the readable part of its label. Enter still closes the preview and restores focus to the launcher.

The four measurements for each edition and preview agree. The normal flow uses the shipped runtime and ordinary browser keyboard events. [Reproduction script](edge_states.py) · [Geometry and hit-testing](edge-states.json) · [Hosted Caspian to Caucasus](667-preview-baku-return-focus-online.jpg) · [Offline Winter across the five](667-preview-overview-return-focus-offline.jpg)

## Candidate identity

| Edition | SHA-256 |
| --- | --- |
| Hosted preview | `d09a0652e7e4c6c3e990420a1f8c675f32c19f29a29b0dabebdad7227f766b71` |
| Standalone | `93e786ba4833e97cdd9e461fe8afd485617e4d7d0f2cbcbb9c2f00651bc92340` |

The local preview returned the exact `docs/index.html` bytes and its `offline.html` matched the root standalone byte for byte. Each edition ran in fresh Microsoft Edge 158.0.4370.33 contexts at 320 × 725, 390 × 844, 667 × 375, 768 × 1024, 1440 × 900 and 2560 × 1440 in English LTR. Touch was emulated. The offline contexts disabled HTTP and HTTPS. The public release was outside this candidate review.

## Passing checks

- At 667 × 375 I opened every photo separately from its gallery thumbnail, decoded the image and checked nine hit points on each of Previous, Next, Download and Close before moving focus or scrolling. All 24 photos passed per edition, all four targets were at least 44 × 44 CSS px and the minimum viewport-edge clearance was 19.84 px. All downloads matched the original assets byte for byte. Close by touch and Escape restored focus to the opener. [Hosted checks](photos-online.json) · [Offline checks](photos-offline.json) · [Landscape photo](667-photo-vienna-online.jpg)
- Across all six sizes, keyboard skip and section links, the compact section menu, budget focus and arithmetic, stay selection, walk and anchor selection, itinerary disclosures, comparison and Sources passed the independent walkthrough. Both previews mounted and showed all eight selectable scenes with reduced motion. The real Globe mounted, selected Prague and opened its chapter, then recovered from a simulated context loss. At 667 × 375 the satellite map and the full Stage artboard fit inside the viewport on their intended entry actions. [Hosted matrix](sizes-online.json) · [Offline matrix](sizes-offline.json) · [Reviewed captures](contact.jpg)
- The shared alignment script measured 573 states per edition with zero document overflow and zero measured alignment spread. Both release suites passed in both editions, covering five cities, ten stays, 37 itinerary days, 55 walking routes, 24 photos, normal preview playback and reduced-motion posters. A4 generation opened all eight Baku days for print and restored the two I had opened. The healthy checks recorded no browser errors or failed assets, and no HTTP requests from the offline contexts. [Hosted alignment](alignment-online.json) · [Offline alignment](alignment-offline.json) · [Premium hosted](premium-online.log) · [Premium offline](premium-offline.log) · [Winter hosted](winter-online.log) · [Winter offline](winter-offline.log)
- With WebGL disabled, both editions kept the flat map, city selection and chapter links. Blocking the Stage script request on the preview displayed the fallback notice, kept winter plans visible and left focus on the launcher with the preview closed. [Hosted fallbacks](fallbacks-online.json) · [Offline WebGL release suite](premium-offline.log) · [Injected runtime comparison](edge-states.json)

## Limits and observations

- Injecting an empty successful HTTP script response or replacing the standalone's embedded Stage script exposed an empty panel with Close preview. Both injected cases still announced the fallback, preserved focus and left the winter plans reachable. Close dismissed the panel and restored launcher focus. The delivered runtime was intact and ran successfully in both editions. This is an additional presentation defect under injected failure.
- The raw alignment script lists inline photo, attribution and research links below 44 px. The dedicated mast, chapter and Sources actions passed the larger target measurements. The reading-length pass found no full-line samples over 75 characters at 320 or 390 px. Wider states included longer provider and accommodation notes, up to 105 characters at 667 px and 159 at desktop widths. The print result covers PDF creation and disclosure state. Physical devices, other browser engines, RTL, external booking or map transactions, and paper output were outside this review. [Hosted alignment detail](alignment-online.json)
