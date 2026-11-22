# Independent dry round 2

**Result. Passed.** A separate reviewer started after round 1 and used a separately written harness and fresh Microsoft Edge 158.0.4370.33 contexts. The live site and offline download matched the round 1 release.

| Artifact | SHA-256 |
| --- | --- |
| GitHub Pages | `33b23d096227cb0d81d10faf76754a0d020488784b027069456d5ec4b6a61bba` |
| Standalone | `e6df97ff7b1a1e404a9a44e6e5fb31015221968ec7185eac5e7f3b284555ae40` |

## Coverage

- Five clean offline file contexts at 320 × 725, 390 × 844, 740 × 360, 768 × 1024, and 1440 × 900. All recorded zero HTTP requests and zero app or console errors. The live 390 × 844 flow issued only same-origin requests. Used the public download control and checked the downloaded file hash. [Edge test trace](premium-evidence/edge-round2.json)
- Compared the itinerary and flight, stay, and route facts against the source dataset. All five cities, ten stay and anchor records, ten flight legs, 37 day sections, 55 mapped walks, 17 licensed photo assets, and 92 source links were exercised or inspected. Verified that the selected stay and unrelated benchmark routes are labeled distinctly. Verified the updated Vienna airport connections.
- Checked tab focus, emulated touch, responsive navigation, photo dialog Escape and focus return, the three typefaces, group and per-adult budget increments, comparison, reload persistence, and reset. Chromium’s print output included all six Prague days and restored the prior disclosure state.
- Inspected actual live globe movement and the offline settled reduced-motion frame. Disabled WebGL and forced context loss both left the flat atlas usable. [Motion recordings](PREMIUM-EXPERIENCE.md#rehearsal-and-compatibility)

The public listing and transit source audit happened separately before promotion. Physical device and assistive-technology sessions were unavailable. Checkout totals and booking availability remain unverified. No material issues were found in the release.
