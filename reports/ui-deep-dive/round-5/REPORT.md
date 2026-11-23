# December, Elsewhere · Independent Edge dry round

**Pass.** Microsoft Edge 158.0.4370.33 on Windows, 23 November 2026. Audited build `d48cd6ef84964e07aa0f4b2388a56a3e74d46ba8` with fresh English LTR browser contexts. Covered 320 × 725, 390 × 844, 667 × 375, 768 × 1024, 1440 × 900, and 2560 × 1440, using emulated touch at the first three sizes and native keyboard input across the sweep.

| Edition | Preview | SHA-256 |
| --- | --- | --- |
| Web | `http://127.0.0.1:18768/` and `http://127.0.0.1:18770/december-elsewhere/` | `7f11a5268987a9e14ad12336378be0e0f160b8ca111b90b58af1978001d51715` |
| Offline | Root `index.html` with networking disabled. The local web download serves the same bytes. | `810972ed812b0dbd348b99f06c95d9f77c356a5af2d48a5397a44a232aa976e4` |

## Results

| Check | Evidence |
| --- | --- |
| Geometry | `measure/audit.py` measured 573 states per edition. Document overflow, measured regional horizontal overflow, and alignment-group spreads were all 0 px. Compare and Evidence shared the same centered rail at each width. [Summary](geometry-summary.json) · [Web measurements](geometry-web.json.gz) · [Offline measurements](geometry-offline.json.gz) |
| Chapters and planning | `verify_premium.py --browser msedge` exercised five chapters, 10 budget-linked stays, 37 itinerary day panels, 55 walking paths with exact provider links, 24 photos with credits, and the Globe and its fallback. Budget edits updated comparison and survived reload. A real A4 PDF was produced and print events expanded then restored the itinerary. [Web](premium-web.log) · [Offline](premium-offline.log) |
| Winter and maps | `verify_winter.py --browser msedge` checked all five satellite map sets, selected-route retention across satellite and diagram, winter choices and photographs, and both Stage previews with normal and reduced motion. The interactive Globe and forced static fallback independently navigated to the selected chapter. [Web](winter-web.log) · [Offline](winter-offline.log) · [Globe](web-667-globe.png) · [Static fallback](web-667-fallback.png) |
| Photo viewer | `verify_ui_layout.py --browser msedge --photos-only` checked the landscape controls for every photo. An independent 667 × 375 sweep tapped every Download control and matched all 24 returned files, authors, source URLs, and license URLs in both editions. At all six widths a representative photo preserved its intrinsic aspect ratio, accepted ArrowRight, and returned focus on Escape. [Web](photos-web.log) · [Offline](photos-offline.log) · [Download hashes](photo-downloads.json) · [Viewer](offline-667-photo.png) |
| Navigation and network | The independent six-size flow used the compact menu by touch and the full-size chapter nav by keyboard. The destination headings received focus and section links changed the hash. The accepted runs recorded zero page, console, or failed-resource errors, and offline runs made zero HTTP requests. Hosted requests stayed on their tested origin. [Interaction record](interactions.json) · [320 px cover](web-320-cover.png) · [2560 px cover](web-2560-cover.jpg) |

## Landscape Stage regression

At 667 × 375 in both editions and both motion preferences, I tapped each preview, tapped its first named scene, and pressed native Shift+Tab from that focused scene button. Close received focus with its entire 116.55 × 44 px box and center hit point available. The 460 × 190 px stage fit alongside it, clear of the sticky chapter bar by 18.43 px. All scene buttons fit above the viewport edge and accepted their center hit points. Tab moved forward again, and closing by Escape or touch restored the originating trigger. The photographs decoded in every manually selected scene, and scene notes cleared the progress track. [Web five-city preview](web-667-overview-focus.png) · [Offline regional preview](offline-667-baku-focus.png) · [Measured boxes](interactions.json)

At 390 × 844, both previews started on Baku and advanced automatically with motion enabled. Selecting Baku manually held the scene past an autoplay interval. Reduced-motion sessions used the final still as the initial frame, with zero Stage animations. An injected exception after a partial mount in each preview left the panel hidden, cleared the busy state, retained trigger focus, and showed “Preview unavailable. Read the winter plans above.” [Autoplay frame](offline-390-baku-auto.png)

## Observations

- Inline provider and photo-credit links account for the measured targets below 44 px. The dedicated source actions, navigation, and Stage and viewer controls met the measured touch-target requirement.
- Open Evidence prose topped out at 72 characters per full line from 667 px upward. Some ancillary stay and walk notes still exceed 75 characters. The longest Vienna alternative stay line was 159 characters at desktop widths, matching the measured pre-change baseline.
- The first winter run on port 18768 hit intermittent connection refusals during concurrent local testing. A fresh retry at that origin and a run on the quieter port 18770 subpath passed with zero runtime or resource errors. The web digest matched at both origins. Premium, geometry, and the scripted photo sweep used port 18768. The retained winter web log and independent interaction checks used port 18770.
