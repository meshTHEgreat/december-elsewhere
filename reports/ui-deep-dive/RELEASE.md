# Mobile guide release

The final candidate is `85a3d52` in the delivery branch. Its local-guide source was implemented in a separate worktree at `b1eae08`. Both delivery files matched that worktree byte for byte before review.

| Artifact | SHA-256 |
| --- | --- |
| Hosted index | `cc8cdb7db4b3e055b16aff121cc69b09838be0ae8b57cb4d25fa40c5e131177c` |
| Standalone and hosted offline download | `97fb156c67024730f0894985a7a27dcf2351d46245720b4e84fec26c4539fe2b` |

## Approval and review history

The owner asked us to proceed with the recommendations and to prioritize phone layouts. Eight items were approved in the published review. The wide-layout and small atlas label study was deferred. The local-guide follow-up was explicitly authorized while the mobile review was underway. [Owner review](https://meshthegreat.github.io/december-elsewhere/ui-review/) · [Decisions](review/decisions.json) · [Implementation](IMPLEMENTATION.md) · [Guide research](guided-research/RESEARCH.md)

1. The first independent audit blocked release when Previous and Next clipped on 19 of 24 photos at 667 × 375. [First audit](round-1/REPORT.md)
2. Chrome passed after the photo fix. Edge then found that Shift+Tab could leave Close preview partly covered by the sticky navigation in both short-landscape briefings. [First repair](round-2/REPORT.md) · [Edge finding](round-3/REPORT.md)
3. The corrected mobile build passed both reviews on the same bytes. The landscape stage, all scene choices and Close now fit together. [Chrome UI review](round-4/REPORT.md) · [Edge UI review](round-5/REPORT.md)
4. The combined delivery passed two fresh independent reviews on matching bytes. Both browsers exercised core flows and measured 663 states per delivery form, including 90 Local guides states. The standalone made zero HTTP requests. [Final Chrome review](final-chrome/REPORT.md) · [Final Edge review](final-edge/REPORT.md)

## Test coverage and limits

- All five destinations, ten priced stays, 55 pedestrian routes, 37 itinerary days, 24 photos and both Stageshow previews passed. Tests covered 320, 390, 667 landscape, 768, 1440 and 2560 CSS px, English LTR, keyboard and emulated touch, reduced motion, Globe fallback, sources and print.
- All 24 photos kept Close, Previous, Next and Download visible at 667 × 375. The local guides choices kept the published itinerary and current budget values available. The exact Baku tour is GetYourGuide item 517765.
- Remaining observations include short inline attribution links, deferred wide-layout and flat-map label changes, and gaps in the Stageshow tool's automated motion sampling. The [rehearsal](motion/REHEARSAL.md) includes sampled frames and real playback. Physical phones, Safari, assistive technology and booking checkout were outside the review.
