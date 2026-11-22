# Independent travel experience review

The review covered keyboard design, visual hierarchy, photograph provenance, decisions a traveler can make, information privacy, and fitness of the delivered single-file package for offline use. The reviewer did not implement the shipped interface.

| Severity | Finding and evidence | Resolution or verification |
| --- | --- | --- |
| High | The selected destination’s budget and date line inherited muted gray on the dark green selector background. Computed WCAG relative contrast was 1.52:1. | The shipped stylesheet adds a scoped pale green override. The revised computed contrast is 8.80:1. |
| Medium | The first city selector implementation focused the replacement button while scrolling it out of view, leaving the next Tab outside the newly visible chapter. | The current city click handler moves focus to its chapter heading and displays a Change city link near the other section links. |
| Medium | A stay without a matching location proxy silently fell back to the first neighborhood. | The current map UI discloses when no anchor is confidently matched and says routes use public starts. Maintain that disclosure whenever source data lacks a precise listing location. |
| Medium | A print command could omit the closed itinerary days. | The current JavaScript expands the remaining days before print and restores their closed state afterward. |
| Medium | JavaScript initially generated the units “min · km” even if both route metrics were missing. | The revised package marks unverified estimates in the label and route note. A dashed segment indicates direction only, while a solid route indicates path geometry. |
| Medium | Package limits mean a listing’s photograph and exact entrance can be unavailable offline. | All lodging cards lead to the original listing for photography and availability. City photos have their own evidence and labels. Confirm redistribution rights before embedding exact accommodation photos. |
| Low | Based on the app’s calculator model, driver and excursion amounts are total group amounts while other visitor costs are per adult. A previous draft made those units easier to miss. | The visible fields label their unit, and the independent runtime test applies a distinct exact group/per-adult increment for each city. |

## Package, accessibility and privacy

The package contains no runtime script sources, image sources or CSS imported over HTTP. Its content security policy prohibits programmatic connections, and external navigation uses HTTPS links with `noopener noreferrer`. The calculator and selections use browser-local storage. No sign-in, credentials, analytics, or traveler identity fields were observed in the reviewed source. Offline integrity checks also checked data-URL photographs for valid WebP container signatures and the presence of author, original URL and license fields.

The review verified labels, keyboard focus treatments, button pressed states, reduced-motion styles, native itinerary disclosures, and a textual alternative to interpreting the map. A source-level review does not establish assistive technology or device compatibility. Browser launch from the local command environment failed when Chromium attempted its startup Unix socket. The browserless audit is recorded separately and is not counted as a full browser dry round.

An independent Pillow decoder loaded all 11 embedded WebP photographs from the generated HTML. Their decoded sizes ranged from 658×1170 to 1680×1120. The ten lodging cards retain separate official Airbnb room URLs and published observations for three adults. The skeptical-traveler evidence check found that Baku is the easiest itinerary to price out first, but a departure-date schedule is still different from three bookable seats. For Tbilisi, the Modern 2BR's published bed configuration better addresses three adults looking to avoid a sofa bed. The indicative options for Budapest and Vienna are easier to compare after accounting for longer one-stop journeys and visa status. Prague has the least complete exact-date flight timings and requires an additional look at the proposed connections.
