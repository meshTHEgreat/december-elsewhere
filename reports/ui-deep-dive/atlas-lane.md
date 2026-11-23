# Atlas lane

## UI-05 | Map and globe

The mobile shortcut now links to a named, focusable map and globe region. It comes beside the destination heading in the reviewed layout. The city list still precedes the map in document order. The route bearings, destination coordinates, and direct-distance calculation are unchanged.

The globe announces loading in the existing status region. If a visitor moves focus out of the atlas, navigates to another fragment, or scrolls away during loading, the atlas releases the loading state. A late script result cannot reopen it or move the visitor. When the globe cannot open or loses WebGL context, the map stays available with the chosen city and distance.

The shared style lane owns the target width, mobile heading layout, and short landscape fit. Measure these on the integrated candidate. This lane does not certify the two independent release rounds.

| Copy | Before | After |
| --- | --- | --- |
| C01 | Explore the destinations | Explore cities |
| C02 | Five trips from Medina, with estimated costs per adult. | Five trips from Medina. Estimates are per adult. |
| C03 | Preview on the atlas | City on map |
| C04 | From MED · Actual flight connections are in each chapter | From Medina. See Arrival for flights. |
| C05 | Back to the atlas ↑ | All cities ↑ |
| C06 | This browser is using the static atlas. | Globe unavailable. Use the map. |
| C07 | The globe was interrupted. The map is still available. | Globe stopped. You can still use the map. |

The earlier request to keep all five cities before the map is respected. Direct distance still describes geographic distance. Arrival keeps the actual flights. No approved atlas work was skipped. The ultrawide rail and phone label collision study remain outside this approved item. [UI-05 proposal](proposals.json) · [Owner decisions](review/decisions.json)

## Checks and commits

- **ddddb09** adds four browser and source-template checks. All four failed against the unchanged guide. They reported a missing shortcut, missing loading messages, and the old WebGL recovery copy.
- **ac311af** changes the test harness only. It waits for the script element to detach before confirming script evaluation through a CSP-safe Playwright expression. The earlier dynamic wait was rejected by the guide's existing script policy. Product CSP stays intact.
- **fc915b6** changes the atlas JavaScript and the source template. It does not contain test or generated artifact changes.
- Chrome 157.0.8103.79 passed all four atlas tests with the rebuilt lane preview. It covered the keyboard shortcut at 320, 390, and 667 px, exact Prague selection and distance, a blocked optional script, successful late script delivery without focus or scroll movement, actual WebGL, and a simulated context-loss event.
- The standalone guide passed a separate focused Chrome check in fresh 320 × 725 and 667 × 375 contexts with networking disabled and reduced motion enabled. Touch opened the shortcut and focused the region. The globe and flat map kept Prague selected. Neither context made HTTP requests or raised page errors.
- The Node package check and JS syntax check passed. The integrated release still needs the shared layout tests and end-to-end verification.
