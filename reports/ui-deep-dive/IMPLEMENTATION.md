# Mobile quality build

The [owner review](https://meshthegreat.github.io/december-elsewhere/ui-review/) published with decision commit `0075d88`. The public guide, downloadable HTML, and app source were unchanged at that commit. Decisions are stored per ID in [the review record](review/decisions.json).

## Worktrees and test order

| Lane | Scope | Tests first | Implementation and report |
| --- | --- | --- | --- |
| App | UI-01, UI-02, UI-03, UI-07, UI-08 markup, navigation, calculator, and data presentation | `fda2d75`, `dd11983` | `82c880b` · [App lane](app-lane.md) |
| Shared style | UI-01 through UI-08 geometry, focus rails, photo viewer, sources and media | `904884d`, `db9aa2b`, `5e6d18a` | `43020ba`, `8ffbca1`, `deb7ce1`, `4d5d334` |
| Atlas | UI-05 shortcut, loading and fallback | `ddddb09`, `ac311af` | `fc915b6` · [Atlas lane](atlas-lane.md) |
| Stageshow | UI-06 active playback, manual scene choice, and short viewport frame | `527e427`, `9a47c96` | `52ef648`, `a120354` · [Stageshow lane](stage-lane.md) |

The first combined render caught a 26.39 px spread between the 320 px budget amounts. The labels now fit one line and the amounts align. A separate landscape scene check caught longer notes touching the Stage progress marks. The final scene CSS leaves space above progress at the same 14 px detail size. Both fixes were tested before their source changes. The [UI change log](UI-CHANGELOG.md) tracks each approved decision. UI-09 was deferred.

## Before and after

| Check | Baseline | Frozen build |
| --- | ---: | ---: |
| Sticky total height at 320 px | 191.67 px | 92.36 px |
| 320 px Cities / Winter target width | 31.7 / 36.1 px | 44 / 44 px |
| Selected city name edge spread | 7.19 px | 0 px |
| Baku stay action top at 390 px | 1216 px | 622.42 px |
| Baku photo frame height at 390 px | 565 px for 242 px of photo | 242.47 px |
| Landscape map after native selection | 0 of 55 complete traces in view | 55 of 55 complete traces in view |
| Globe cut off at 667 × 375 | 178.8 px of the visual | 0 px of the visual |
| 667 × 375 preview displayed | 271 of 365 px | Full 460 × 190 px scene and focused Close |
| Sub-44 px targets in measured nav and opened Sources | Reported in per-area audits | 0 |
| Document overflow in the alignment matrix | 0 px | 0 px across 573 states |

The 320 px budget focus check verified clearance below the bars and maximum values without splitting amounts. Comparison retained zero sideways scroll. Inline attribution links in prose are still listed in the raw target audit. The larger source and license actions are in the Sources disclosures.

The visual direction follows Taste Skill v2. Trip photos run to the viewport edge where they set the scene. Comparison, evidence and stays use shared rails and rules with minimal fills. The budget total keeps its distinct surface because it follows the visitor during entry. The Stageshow tool frames and real host captures are documented separately.

The installed Taste browser inspector confirmed the cover action fits at all six sizes, with zero horizontal document overflow. Its section-height and grid heuristics still flag the custom mast, the short evidence band, and selected uneven column widths. At 667 × 375 the cover action is in view and the full cover extends 13 px past the fold. The tests retain the deliberate document rhythm and phone tap geometry. [Taste inspector results](measure/taste-layout-final.json)

[Before and after measurements](measure/mobile-recheck.json) · [Actual phone and landscape shots](measure/shots/) · [Alignment audit script](measure/audit.py)

## Payloads

No numeric budget was tracked in the baseline. Both optional scripts remain on demand. The globe bytes match the baseline. This table uses the same local gzip level for both revisions.

| Asset | Before raw / gzip bytes | After raw / gzip bytes |
| --- | ---: | ---: |
| Hosted HTML | 472,669 / 136,028 | 483,704 / 138,649 |
| Inline CSS | 53,263 / 12,627 | 57,457 / 13,427 |
| Inline JS | 47,908 / 15,422 | 54,605 / 17,453 |
| Optional Stageshow JS | 183,235 / 61,787 | 184,042 / 62,084 |
| Optional Three.js globe | 515,077 / 130,312 | 515,077 / 130,312 |
| Standalone file | 8,327,380 / 5,742,564 | 8,339,252 / 5,746,089 |

The build kept the travel, pedestrian path, satellite, photo, outdoor and winter data files byte-identical to the baseline.
