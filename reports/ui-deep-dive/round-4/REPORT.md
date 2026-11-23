# Independent Chrome review 4

**Pass on candidate `d48cd6e`.** The hosted package was served on the production-shaped path `http://127.0.0.1:18770/december-elsewhere/`. The standalone `index.html` was opened with networking disabled. Chrome 157.0.8103.79 used fresh contexts and emulated mobile touch input. I started with the 667 × 375 preview regression and visually inspected four browser captures.

| Package | Verified SHA-256 |
| --- | --- |
| Served `docs/index.html` | `7f11a5268987a9e14ad12336378be0e0f160b8ca111b90b58af1978001d51715` |
| Standalone `index.html` and downloadable `docs/offline.html` | `810972ed812b0dbd348b99f06c95d9f77c356a5af2d48a5397a44a232aa976e4` |

## Mobile findings

- At 667 × 375, I opened both winter previews by touch, selected the first scene, then pressed Shift+Tab. Close received keyboard focus, remained entirely visible, and passed hit-testing at the center and four inset corners. Its bounds were y=122.02–166.02 px, below the sticky navigation at y=103.59 px. The stage remained within y=122.02–312.02 px. All three or five scene buttons were 44 px high and fully hit-testable, ending at y=366.41 px. Escape and touch dismissal each restored focus to the opening control. [Caspian to Caucasus capture](667-baku-reverse-focus.png), [Winter across the five capture](667-overview-reverse-focus.png).
- Both previews automatically advanced from Baku with normal motion at 390 × 844, and a manual return to Baku held for another complete scene interval. Reduced motion showed the final scene immediately and allowed each scene to be selected with the keyboard. An injected runtime mount failure closed the panel, left the trigger focused, cleared the busy state, and announced that the preview was unavailable. [Hosted measurements](independent-web.json), [standalone measurements](independent-offline.json).
- At 667 × 375, both editions displayed usable Close, Previous, Next and Download controls for all 24 photos. I cycled each city's gallery by touch, checked backward and forward wraparound, and downloaded each photo. All 48 downloads had the expected filename and matched the packaged bytes. Closing the viewer restored focus. [Hosted photo results](independent-web-photo_actions.json), [standalone photo results](independent-offline-photo_actions.json).
- The compact layout passed at 320, 390, 667, 768, 1440 and 2560 px. The five city titles shared a left edge, the atlas wrapper was centered within 0.02 px, the measured navigation targets were at least 44 px, and the cover facts fit in the first viewport. The two budget amounts shared a baseline at 320 and 390 px. [320 × 725 cover](320-cover.png), [hosted layout suite](layout-web.log), [standalone layout suite](layout-offline.log).
- At 390 × 844, the keyboard shortcut focused the atlas and Tab reached its city picker. The live globe selected Vienna and released its canvas on chapter entry. With WebGL forced unavailable, the flat map stayed usable and took the same route into Vienna. The 320 px planning flow reflected an edited cost in Compare, then printed eight Baku days and restored the original disclosure state. [390 × 844 globe](390-mobile-globe.png), [hosted measurements](independent-web.json), [standalone measurements](independent-offline.json).

## Release suite results

| Check | Hosted | Standalone |
| --- | --- | --- |
| Premium default matrix at 1440 × 900, 390 × 844 and 740 × 360 | Pass | Pass |
| Winter default matrix at 320 × 725, 390 × 844, 667 × 375 and 1440 × 900 | Pass | Pass |
| Six-width layout and 667 × 375 photos | Pass | Pass |
| `verify_ui_layout.py --photos-only` | Pass | Pass |
| Mobile application navigation, budget, walks, stays and Compare | Pass | Pass |
| Independent mobile interaction, geometry, photo downloads and failure recovery | Pass | Pass |

Every premium viewport exercised five chapters, 55 walking routes, 10 stays, 37 itinerary days and 24 photographs. Every winter viewport exercised both previews and satellite imagery across all five cities. The final suites recorded no page errors, console errors or HTTP errors. The standalone sessions made zero HTTP requests. Hosted traffic stayed on the preview origin. [Hosted premium](premium-web-subpath.log), [standalone premium](premium-offline.log), [hosted winter](winter-web-subpath.log), [standalone winter](winter-offline.log).

## Earlier attempts

The initial parallel run against `127.0.0.1:18768/` recorded a photo decode error and a Budget deep-link focus timeout in the hosted package. Both checks passed on immediate rerun against that URL and again against the subpath preview. The initial hosted premium and winter matrices and the standalone counterparts also passed. The two failures were unreproduced with the same candidate bytes and their cause was unconfirmed. [Initial photo trace](photos-web.log), [initial focus trace](mobile-app-web.log), [passing hosted photo retry](photos-web-subpath.log), [passing hosted mobile app retry](mobile-app-web-subpath.log).

An early independent alignment assertion treated the desktop city column as the entire atlas. I corrected the probe to measure the centered atlas wrapper and separately assert the shared city-title edge. No product files were changed during this review. [Independent Chrome check](chrome_review.py).
