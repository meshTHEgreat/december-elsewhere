# Verification record | 23 November 2026

## GitHub Pages release candidate

- SHA-256 `23a10ce194e12462028f238965327a4cfad439f37bed38caf25767cd55276450`. A fresh Windows build reproduced the ZIP's `index.html` byte for byte.
- Fresh offline `file://` sessions in Chrome 157.0.8103.79 and Edge 158.0.4370.33 passed at desktop, tablet and phone widths. Extended desktop and phone checks decoded all 11 photographs, selected all 55 map routes from ten starting points, expanded all 37 itinerary days and selected all ten primary stays.
- Keyboard and emulated touch navigation passed. Budget, stay and comparison selections survived reload, reset restored defaults, and the phone budget summary stayed pinned. Desktop print generated a PDF, expanded the itinerary and restored disclosure state afterward. No app errors or HTTP requests occurred in the offline runs.

## Mobile-first revision

**Release SHA-256** `23a10ce194e12462028f238965327a4cfad439f37bed38caf25767cd55276450`  
**Standalone size** 4,034,341 bytes.  
**Strict dry-round gate** 0 of 2. The browser previews use local HTTP.

| Check | Observed result |
| --- | --- |
| Layout | Frames set to 320, 390 and 768 CSS px. Each fit all five city rows on the opening screen at 725, 844 and 900 px height respectively. Page widths matched the usable viewports, with no horizontal overflow. |
| Navigation | Enter selected the city and focused its heading. Walk and itinerary jump links worked on narrow screens. Changing Vienna’s walking anchor and route showed 18 min and 1.36 km. The last itinerary day opened from the keyboard. |
| Budget | On a 390 px frame, adding SAR 101 to the per-adult meal allowance and SAR 250 for a shared car changed Baku from SAR 12,029 to SAR 12,582. Its per-adult selector showed SAR 4,194. The comparison displayed the same group total. The summary remained pinned below the header while editing. |
| Persistence | Budget and Prague comparison persisted on reload. Reset restored SAR 12,029 and collapsed the car section. No app console errors appeared in the managed preview. |
| Desktop preview | All five cities opened using Enter, and Next photo advanced the gallery in every city. |
| Standalone checks | Both isolated-runtime harnesses passed again. All 55 walking routes, 37 itinerary days and 11 photos are retained. No em dashes occur in the packaged text. |

## Previous release

**Release SHA-256** `4e1d3f2247f8998aeb93c77ca38f40da4e8ac9ff5ef2f2792927f3de09222379`  
**Strict gate** Open, 0 of 2 qualifying dry rounds.  
**Size** 4,032,336 bytes for the complete standalone file.

| Check | Observed result | Gate status |
| --- | --- | --- |
| Primary Chrome preview | Used Enter through all five cities, changed each photo, opened each second day and selected map routes and anchors. All chapter images decoded. Baku second stay wrote SAR 1,343, SAR 800 per adult for meals produced SAR 12,254, and reload preserved it. Prague comparison and reset to SAR 12,029 passed. Final route refresh showed real path geometry across all five guides. No application error appeared in console logs. | Passed on local HTTP preview. |
| Independent Chrome preview | Fresh tab, separate reviewer, same browser profile. Used Space through all five cities, checked heading focus, decoded galleries, expanded each last day, exercised alternate walking anchors, incremented shared and adult budget fields, changed Prague lodging and comparator, reloaded. See the independent Chrome report. | Passed on local HTTP preview. |
| Phone and tablet layout | Chrome frames set to 390 and 768 CSS px. With scrollbars the inner layout widths were 375 and 753 px. Document scroll width matched each viewport. All five city buttons were present. Clicked Prague, rendered the chapter and decoded the hero at both widths. | Passed layout and pointer checks. Physical touch and screen reader behavior remain unverified. |
| Independent isolated-runtime checks | Two separate reviewers evaluated the packaged HTML in separate Node VM harnesses without network APIs. Both tested all five guides and calculator behavior. All 11 embedded WebP images, 55 walking paths, 37 itinerary days and 10 primary lodging entries passed the applicable package checks. The second compile was byte-identical. | Passed package checks. |
| Clean disconnected browser opening | The managed Chrome browser permits HTTP and HTTPS navigation and denied the standalone local-file URL. Chromium in the shell exited before navigation on a required Unix socket operation. The packaged Playwright script is available for a compatible test environment. | Blocked. Both strict rounds are still pending. |
| Booking links and inventory | Travel research contains date, source and status. Independent public rechecks opened 7 of 10 exact Airbnb entries. Both retained Vienna links and Prague Cozy Home 2 could not be retrieved in that recheck. One Vienna fallback was verified at listing level. Exact checkout, aircraft inventory and third-party link availability remain variable. | Partial external evidence. |
| Accommodation photo rights | No redistribution license was established for the retained Airbnb images. Original pages carry the exact galleries where retrievable. Eleven licensed destination pictures are embedded. | Rights constraint documented. |
| GitHub Pages | No authorized GitHub Pages repository was established for public deployment. | Optional. |

A valid first round and a separately repeated second round must each run the standalone artifact in a fresh browser with networking disabled. Include desktop and mobile viewports, inputs, route actions, all itinerary and gallery states, storage, print, browser logs and asset load evidence. Restart the count after any material defect. Official flight and entry details should be rechecked before booking.
