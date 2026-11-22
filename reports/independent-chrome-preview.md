# Independent managed Chrome preview

**Artifact** `index.html`, SHA-256 `4e1d3f2247f8998aeb93c77ca38f40da4e8ac9ff5ef2f2792927f3de09222379`

The reviewer opened a new Chrome tab to the local preview server and reloaded after the final data build. Tests used the standard rendered controls. This context used the existing managed browser profile. It did not run a fresh isolated profile, a disabled-network `file://` round, or mobile touch emulation. It therefore counts as an independent preview check, not a full strict dry round.

| City | Keyboard | Second anchor, last walk | Gallery render | Itinerary |
| --- | --- | --- | --- | --- |
| Baku | Space on selector focused Baku heading | Sahil metro, 24 min / 1.91 km | Hero and alternate loaded | Final day opened with Enter |
| Tbilisi | Space focused Tbilisi heading | David Aghmashenebeli Avenue, 20 min / 1.67 km | Hero and alternate loaded | Final day opened with Enter |
| Budapest | Space focused Budapest heading | Bartók Béla Boulevard cafés, 14 min / 1.02 km | Hero and alternate loaded | Final day opened with Enter |
| Vienna | Space focused Vienna heading | Danube Island near Reichsbrücke, 15 min / 1.20 km | Hero and alternate loaded | Final day opened with Enter |
| Prague | Space focused Prague heading | Prague Main railway station, 21 min / 1.72 km | Hero and alternate loaded | Final day opened with Enter |

- The Prague group calculator moved from SAR 12,652 to SAR 12,921 for a SAR 269 group rental. Adding SAR 53 per adult to airfare raised the group total to SAR 13,080. Selecting the second stay changed the total to SAR 13,642. Reload preserved the selected city, updated total, and Vienna comparison.
- Captured console diagnostics were from the managed browser extension. The application did not emit a captured error.
- The 1,363 px viewport had no document-wide horizontal overflow.
- The alternate Tbilisi photograph and the credit caption were visually inspected. All five chapter and alternate images completed in Chrome and had nonzero dimensions. Separately, all 11 embedded WebPs decoded with Pillow from the HTML bytes.
- A fresh, browserless Node rerun on the same artifact exercised all 55 routed path selections, all ten starts, group and per-adult cost changes across all five cities, stay selection, comparison, reset and storage restoration. The Node report does not validate browser layout, touch or screen-reader behavior.
