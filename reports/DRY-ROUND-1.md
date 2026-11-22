# Independent dry round 1

**Result. Passed.** The creative reviewer used fresh Chrome 157.0.8103.79 sessions. The engineering reviewer independently verified the same frozen release and ran the performance and GPU checks.

| Artifact | SHA-256 |
| --- | --- |
| GitHub Pages | `33b23d096227cb0d81d10faf76754a0d020488784b027069456d5ec4b6a61bba` |
| Standalone | `e6df97ff7b1a1e404a9a44e6e5fb31015221968ec7185eac5e7f3b284555ae40` |

## Coverage

- Live GitHub Pages and disconnected standalone. Desktop 1440 × 900, tablet 768 × 1024, phone 390 × 844 and 320 × 667, and landscape 667 × 375. Checked the cover, menus, chapter section anchors, retained focus, keyboard, emulated touch, and reflow. [Hosted test trace](premium-evidence/live-round1.json) · [Offline test trace](premium-evidence/offline-round1.json)
- All five chapters, 17 decoded photos, all ten stays, 37 day sections, and 55 walking paths. Checked flight and route disclosures, price transfer to budget, calculator changes, comparison, reset, browser persistence, gallery controls and desktop print.
- Inspected actual scene pixels, a rotating globe, and the intermediate walking trace. Normal motion animated and idled. Reduced motion drew one settled globe frame per selection. Denying WebGL or forcing context loss returned to the flat atlas. The creative reviewer approved the photographic sequence, distinct scene crops, and purposeful motion. [Desktop stills](premium-evidence/chapter-contact-1440.jpg) · [Phone route frames](premium-evidence/route-motion-390.jpg)
- No app errors or failed resource requests. The standalone made zero HTTP requests. All 26 served documents and media matched the frozen package, and the browser download matched the standalone. MED and all displayed direct distances were independently checked. [Asset and airport checks](premium-evidence/assets-and-airport.json) · [Build parity](premium-evidence/frozen-parity.json)
- The exact hosted build was measured in Chrome at 390 × 844 with 4× CPU throttle, 1.6 Mbps downstream, and 150 ms latency. Median normal-motion LCP was 2.25 seconds. Median city readiness was 1.84 seconds. [Performance results](premium-evidence/live-render-perf.json)

No material defects were found on the tested release. Mobile and tablet input used browser emulation. Booking inventory and checkout were outside this round.
