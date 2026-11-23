# Winter preview rehearsal

The guide retains the installed Stageshow Stage and Act runtime. The editor frames a single photo and one decision at a time, with an opt-in sequence. The new scene buttons stop automatic advancement and show a specific place. At short landscape heights, the same sequence uses a 460 × 190 stage with 14 px detail text.

## Captures

- **Caspian to Caucasus.** Baku, Shahdag, Tufandag. Film at 390 px and actual host recording at 390 × 844. [Baseline frames](baseline-baku-390.jpg) · [Final frames](final-baku-390.jpg) · [Guide recording](ui-preview-baku-390.webm)
- **Winter across the five.** Baku, Tbilisi, Budapest, Vienna, Prague. Film at 1024 px and actual landscape host recording at 667 × 375. [Baseline frames](baseline-overview-667.jpg) · [Final frames](final-overview-1024.jpg) · [Guide recording](ui-preview-overview-667.webm)
- Inspected opening, handoff and settled frames. The photo begins its crossfade before the note settles. In short landscape, Close sits beside the artboard. Tab advances from Close to named scenes, and Shift+Tab returns to a fully visible Close. [Keyboard-focused screenshot](../measure/shots/667-winter-keyboard.jpg)

## Findings and limits

- A longer title and note at short landscape touched the progress row when the browser's paragraph margins used the old spacing. The all-scenes browser check went red before resetting the margin on the shallow stage. All eight scenes then cleared the progress marks.
- The Stageshow framing gate produced zero findings in both final sheets. Automated temporal coverage was inconclusive because five sampling gaps per film exceeded 11 ms. Use the frame sheets and direct recordings alongside the browser play, manual, reduced-motion and rotation checks. [390 gate output](final-baku-390.json) · [1024 gate output](final-overview-1024.json)
- The framing sheets crop to the Stage artboard. The host recordings and [layout recheck](../measure/shots/) show Close, the fixed navigation and the manual scene buttons. Devices were emulated.
