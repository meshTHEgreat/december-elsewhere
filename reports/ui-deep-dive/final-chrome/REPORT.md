# Final combined Chrome review

**Pass in both editions.** I reviewed the combined `b1eae08` candidate with Chrome 157.0.8103.79 in fresh contexts, starting at mobile widths. The hosted build ran at `http://127.0.0.1:18771/december-elsewhere/`. The standalone edition ran with networking disabled.

| Package | SHA-256 |
| --- | --- |
| Hosted HTML, hashed from the browser response | `cc8cdb7db4b3e055b16aff121cc69b09838be0ae8b57cb4d25fa40c5e131177c` |
| Standalone HTML and identical downloadable copy | `97fb156c67024730f0894985a7a27dcf2351d46245720b4e84fec26c4539fe2b` |

## Local guides

- All five Itineraries start with the optional Local guides section collapsed. At 390 × 844, I opened it by touch and switched between Day trip and Stay overnight with the keyboard. The two plans opened one at a time, the original itinerary still had 8, 7, 8, 8 and 6 days, and the budget inputs and totals stayed the same in every chapter. **Update the budget** moved keyboard focus to Budget. The optional disclosure was hidden in print. [Hosted sample](sample-web.json), [standalone sample](sample-offline.json).
- Baku’s Day trip rendered Gobustan, Absheron and the canonical `t517765` GetYourGuide listing. Its Stay overnight alternative rendered the route through Qusar or Shahdag, with Laza conditional on opening. I visually inspected both captures and hit-tested the booking link. [Baku day trip](390-baku-guide-day.png), [Baku overnight](390-baku-guide-night.png).
- The guided suite passed all five cities at 320 × 725, 390 × 844, and 667 × 375, including direct `#city/guides` focus. The shared audit covered 663 states per edition, 90 of them guide states, at 320, 390, 667, 768, 1440 and 2560 px. No horizontal document overflow or measured alignment spread over 1 px was reported. Every measured guide control was at least 44 px in both dimensions. The audit also recorded 750 instances per edition of existing inline text links below the 44 px threshold, with identical findings across editions. [Hosted guided suite](guides-web.log), [standalone guided suite](guides-offline.log), [audit summary](audit-summary.json), [hosted raw data](audit-web.json.gz), [standalone raw data](audit-offline.json.gz), [inline-link measurements](inline-link-measurements.log.gz).

## Core guide and landscape regressions

| Check | Hosted | Standalone |
| --- | --- | --- |
| Premium, three default viewports | Pass | Pass |
| Winter, four default viewports | Pass | Pass |
| Photos-only at 667 × 375 | Pass | Pass |
| Live landscape preview and independent photo actions | Pass | Pass |
| Globe, flat-map fallback, Budget, Compare and PDF printing | Pass | Pass |

The premium sweep covered five chapters, 55 walking routes, ten stays, 37 days and 24 photographs at each viewport. At 667 × 375, Shift+Tab brought focus to a fully visible, hit-testable Close button in both winter previews after I selected the first scene. Close occupied y=122.02–166.02, the stage ended at y=312.02, and all scene controls fit through y=366.41. The injected preview mounting failure shut the panel and kept focus on the trigger. [Hosted premium](premium-web.log), [standalone premium](premium-offline.log), [hosted winter](winter-web.log), [standalone winter](winter-offline.log).

All 24 landscape photo downloads in each edition matched the packaged bytes. Touch cycling, wraparound and focus return worked. An edited budget still updated Compare to SAR 4,354 per adult, and printing expanded all eight Baku days before restoring the original state. Browser checks recorded no page, console or HTTP errors. The offline edition attempted zero HTTP requests, and hosted requests remained on the preview origin. No product files were edited in this review. [Hosted photos-only](photos-web.log), [standalone photos-only](photos-offline.log), [hosted independent evidence](sample-web.json), [standalone independent evidence](sample-offline.json).
