# Destination chapter walkthrough

Chrome 157.0.8103.79. Local Pages build at commit `6f017c5`. English, left to right. Each width used a fresh context. The main pass measured 101 states at each width across Baku, Tbilisi, Budapest, Vienna, and Prague. It covered arrival, flight details, both priced stays, available alternate stays, both basemap styles and public anchors, winter choices, itinerary disclosures, photo dialog, and chapter ending. Baku hosts the chapter-independent checks of both winter films, because every chapter uses the same two film sequences. The action pass separately measured all 55 walk choices at each of the three widths with a visible native picker.

The measurement file contains the sections, interactive rectangles, alignment groups, and lines from per-character Range rectangles. Character counts use trimmed rendered whitespace. Text sort and first-line alignment compare rect centers to allow the browser’s inline type differences. Native select content uses canvas text widths and an 18 px chevron reserve. The native control’s true content clip varies by browser, so overflowing text width is a screen for inspection, not a claim that the browser uses a particular pixel for an ellipsis.

[Measurement data](chapter-measurements.json.gz) · [Action edge data](chapter-action-edges.json) · [Browser runner](measure_chapters.py) · [Range and alignment code](chapter-measure.js) · [Action runner](measure_edges.py)

## Rails and first view

| Viewport | Shared chapter content | Empty space per side | Baku map panel | Baku winter photo and copy | Documentary evidence |
| --- | ---: | ---: | ---: | ---: | --- |
| 320 × 725 | 288 px | 16 px | 288 px | 288 px, stacked | [Walk](shots/baku-320-walk-controls.jpg) · [Winter](shots/baku-320-winter-1.jpg) |
| 390 × 844 | 357.23 px | 16.38 px | 357.23 px | 357.23 px, stacked | [Walk](shots/baku-390-walk-satellite.jpg) · [Winter](shots/baku-390-winter-1.jpg) |
| 667 × 375 | 610.97 px | 28.02 px | 610.97 px | 610.97 px, stacked | [Walk](shots/baku-667-walk-controls.jpg) · [Flight](shots/baku-667-flight-open.jpg) |
| 768 × 1024 | 703.48 px | 32.25 px | 368.22 px | 703.48 px, stacked | [Walk](shots/baku-768-walk-satellite.jpg) · [Winter](shots/baku-768-winter-0.jpg) |
| 1440 × 900 | 1232 px | 104 px | 653.61 px | 587.2 px per column | [Arrival](shots/baku-1440-arrival.jpg) · [Winter](shots/tbilisi-1440-winter-0.jpg) |
| 2560 × 1440 | 1232 px | 664 px | 653.61 px | 584 px per column | [Walk](shots/baku-2560-walk-satellite.jpg) · [End](shots/baku-2560-end.jpg) |

No one-sided rail drift or document overflow appeared. The 2560 px content rail occupies 48.1% of the viewport. The dark full-width ending already makes the wide chapter feel open. The pale map enclosure emphasizes the narrow center on a wide display. A full-width, low-contrast background band could carry this section without widening the copy or altering paths. A same-brand secondary surface is sufficient. No new color token is needed. Make the map and notes share the established text rail on ordinary screens.

## Findings ranked for travelers

### CH-01 | A walk change hides the entire trace in short landscape

**High impact.** After a route choice at 667 × 375, 0 of 55 path traces are visible beneath the sticky nav. Only 13.3–14.1 px of the 341.4 px map frame is exposed. The picker retains focus. At 320 and 390 px, all 55 traces fit in view under the measured post-choice scroll position, with 153 px and 193.4 px of map visible.

The phone chooser repeats the minutes already shown in Selected walk. At 320 px, its usable width is about 250.4 px. Eight of 55 full options exceed it. The Port Baku option uses 269.1 px, including its time. Its title alone uses 219.8 px. Dropping repeated time reduces the count to two. Those place names use 253.8 px and 287.3 px, so keep the full wording in the selected summary and use accurate short chooser labels. At 390 px, the chooser has 319.4 px of usable room. One label reaches 335.5 px with time, and all fit without it.

Propose a short-landscape split with chooser and summary beside the map. Aim for at least 90% of the map and the complete trace visible after a change at 667 × 375 across all 55 routes, with a reachable and visibly focused picker. Keep the offline estimate, route provenance, public anchor, both directions links, and the real satellite view. Show the current walk once as a summary. The exact owner request says “I want the path to be shown better with real satellite or terrain.” The winter decision log also requires preserving the diagram and external maps.

[320 px selection](shots/baku-320-walk-choose.jpg) · [390 px selection](shots/baku-390-walk-choose.jpg) · [667 px selection](shots/baku-667-walk-choose.jpg)

### CH-02 | Stay actions require an extra screen at every phone width

**High impact.** From direct stay links, the top of the first “Use in budget” action lies between y=1166 and y=1510 at 320 × 725 and y=990 and y=1250 at 390 × 844. All five require scrolling to act. Baku's 304 px outdoor panel at 390 px precedes the two priced options. Price first appears at y=772, while choice starts at y=1216. At 1440 × 900, both stay columns appear, but all five first actions start below the viewport at y=974–1068.

Tbilisi's two stay cards share a top and action edge within 0 px. Price lines differ by 55.28 px at 768 and 41.47 px at 1440, caused by unequal title lines. At 768 px the other split rows also shift prices by 27.64 px in Baku, Vienna, and Prague. The card actions align as designed on these widths.

Move the dated price, bedrooms and beds, outdoor access, listing link and budget action before the related booking caveats. Place the optional outdoor alternative after the priced choices and keep each card's outdoor status near the main details. Use a shared price row or a subgrid to retain alignment for differently wrapped property titles. Keep genuine public listing names and photos links. The owner said “Also prefer stays with somesort of outdoor environment.” Preserve that preference and show verified, listed, or unverified access before the travel actions.

[Baku 390](shots/baku-390-stays-jump.jpg) · [Prague 320](shots/prague-320-stays-jump.jpg) · [Tbilisi 768](shots/tbilisi-768-stay-first.jpg) · [Tbilisi 1440](shots/tbilisi-1440-stay-first.jpg)

### CH-03 | Photo gallery chrome consumes most of the phone dialog

**Medium impact.** On Baku's first photo at 320 px, the fixed frame is 296 × 486 px but the contained image is 296 × 196 px. This creates 290 px of vertical letterbox and puts the arrow buttons at y676–720 with 7 px of internal modal scroll. At 390 px the box is 366 × 565 px and actual image is 366 × 242 px, leaving 323 px of letterbox. The arrows start at y762. Prague's wider image leaves 358 px at 320 or 407 px at 390. The dialog supports keyboard cycling and restores focus to the opener.

Use intrinsic photo geometry with a viewport cap, rather than a large fixed height. Give arrows, close and download a clear control rail. Let captions wrap to a consistent measure below. Maintain native Escape and Arrow keys, image fidelity, each credit, and direct download. At 667 × 375 the actual image is 184 px high. Baku's 277 px width is intentional at that image ratio, with 350 px lateral letterbox. Preserve this landscape ability to fit the image and the 44 px controls together.

[Baku 320](shots/baku-320-photo-open.jpg) · [Baku 390](shots/baku-390-photo-open.jpg) · [Baku 667](shots/baku-667-photo-open.jpg) · [Prague 1440 caption](shots/prague-1440-photo-dialog.jpg)

### CH-04 | Secondary reading runs range from cramped to very long

**Medium impact.** At 320 px, most lead, help and body lines span about 31–46 characters by necessity. Keep the readable font and reduce duplicate wording, instead of shrinking text to reach the 60–75 target. On the 667 px single column, Prague flight help reaches 96 characters, Tbilisi winter credits reach 99, and a Tbilisi itinerary backup reaches 101. At wide desktop, Vienna walking credits reach 105 and Prague's enlarged modal credit reaches 179. Ordinary short statuses and trailing lines are not reading failures. The flight label and same-airport status are separate facts, even when copy gets shorter.

Prefer the existing 52ch section measure for full-line help with repeated use. Constrain long provenance captions separately by separating the factual caption and the source/license links. Preserve the credited author, historical information, and uncertainty. At 320 px Prague has isolated last words “contrasts” and “home” in two itinerary titles. “Old and New Town” and “Fly home” are plain candidates for the copy review. Itinerary date and title rails are already aligned to 0 px across the six Prague days.

[Prague flight 667](shots/prague-667-flight-open.jpg) · [Tbilisi winter 768](shots/tbilisi-768-winter-0.jpg) · [Walk credit 2560](shots/baku-2560-walk-satellite.jpg) · [Prague photo caption 1440](shots/prague-1440-photo-dialog.jpg) · [Prague itinerary 320](shots/prague-320-itinerary.jpg)

### CH-05 | Winter film opens under the sticky navigation in landscape

**High impact.** Opening the Baku film at 667 × 375 initially exposes 271 of 365 px of the frame. The focused trigger is fully covered by the sticky chrome, with 0 of 44 px visible. The first Tab scrolls to the other film button and leaves 122 px of the frame visible. At 320 and 390 px the full 299 px and 365 px frames respectively are visible. Actual playback advances from Baku to Shahdag at 390 and 667 px. Escape closes the stage and restores the trigger at all six sizes.

Use the existing Stageshow landscape-supported wide layout with a shorter frame and a deliberate focus target when opened. Keep the 44 px close button visible in the same view. A 460 px wide frame has about 211 px of height. This leaves room for the close action under the two sticky bars. Keep the compact composition on phones in portrait. Persistent film status should stay near the triggers. The resize-safe fallback should guide the traveler to the still guide above and offer a clear retry when appropriate.

The controlled module load produced “Loading visual briefing” followed by the current failure message at all six sizes. The status is 26 px tall when one line. At 2560 × 1440 only 10 px of either status is in view after focus moves to the triggers at the bottom of the screen. At 390 px the error wraps to 53 px and is fully visible. These are intercepted test responses from the local server, not deployment failures.

[667 px playing](shots/baku-667-stage-open.jpg) · [390 px playing](shots/baku-390-stage-open.jpg) · [Loading](shots/baku-390-stage-loading.jpg) · [Load error](shots/baku-390-stage-error.jpg) · [State measurements](stage-states.json) · [State runner](measure_stage_states.py)

## Touch, alignment, and states

- Primary stay, walking, winter, and photo navigation controls measured at least 44 px in their primary axis in the sampled action states. The short-landscape issue above is an exposure problem. Separate the minor inline provenance targets from that issue. Flight source links measured 18 px high, a map “Scene” link 17 px, and photo source/license links commonly 18 px. Convert repeated provenance groups to separated actions or an accessible details region if a change is approved. Keep all URLs and captions. [Flight links](shots/baku-667-flight-open.jpg) · [Walk source](shots/baku-390-walk-satellite.jpg) · [Photo sources](shots/baku-320-photo-open.jpg)
- Text contrast against flat backgrounds is 6.73:1 for muted on paper, 6.10:1 for muted on the map panel, 6.65:1 for the winter status, 11.83:1 for the Google Maps action, and 16.66:1 for photo dialog text. These ratios use the actual foreground and flat surface colors. No single ratio applies to the photographed cover, and no cover-wide numeric pass is claimed. [Walk controls](shots/baku-390-walk-satellite.jpg) · [Winter choice](shots/baku-390-winter-1.jpg) · [Dialogue](shots/baku-390-photo-open.jpg)
- Measured split winter layout starts photograph and copy on the same rail at 1440 px with 0 px vertical spread. Walk list time right edges and route name left edges also have 0 px spread. The winter photo preceding conditions at 390 px moves the headline 411.5 px below the photo start in Baku. Add resort status before the large photo on narrow view when improving progressive disclosure. Keep the credited scenery and the full conditions. [Wide winter](shots/tbilisi-1440-winter-0.jpg) · [Narrow winter](shots/baku-390-winter-1.jpg)
- Chapter opens put focus on the chapter title. Both priced options, satellite and diagram, two public anchors, all itinerary day data and gallery state remain available. The winter audit covered Baku, Shahdag and Tufandag plus each of the other cities' rendered options. Empty route and unverified options were considered distinct. Every public stop path was present. The application exposed unverified start warnings in cities with approximate anchors, so no “no route” state could be reached with this dataset. [Public anchor and map](shots/vienna-1440-walk-second.jpg)
- All 37 day sections can expand. The opening day already expands by default. Preserve that state and the owner-requested offline itinerary. The chapter ending exposes a useful next destination and comparison. [Expanded itinerary](shots/prague-1440-itinerary-expanded.jpg) · [Chapter ending](shots/baku-1440-end.jpg)
