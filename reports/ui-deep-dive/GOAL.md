# December, Elsewhere UI deep dive

Use the travel journal to choose a destination and make a trip plan on a phone or a wide screen. Tighten alignment and simplify the words while preserving the imagery, live planning tools, factual sources, and offline delivery.

## Baseline

- Commit `6f017c54f0a6ad67ec4db8ab53d2cff767caf361`. Hosted version at `http://127.0.0.1:18768/` during the review and the existing GitHub Pages URL. Offline source is the root `index.html`.
- Test English, left-to-right, at 320 × 725, 390 × 844, 667 × 375, 768 × 1024, 1440 × 900, and 2560 × 1440. Record browser, state, and capture in each review.
- The design system is `source/styles.css` with trip-specific rules in `source/winter.css` and the existing Stageshow typography and scene CSS. Reuse the palette, type, spacing, rules, and photographic assets.
- Preserve five cities, 37 itinerary days, 55 sourced pedestrian routes, 10 budget-linked stays, direct map and booking links, 24 downloadable credited photographs, and documented outdoor-access and winter caveats. Cite the owner's earlier requirements when a change conflicts with one. [Prior acceptance criteria](../PREMIUM-EXPERIENCE.md) · [Winter and satellite decisions](../WINTER-FIELD-GUIDE.md)
- Compare one-day outings and overnight bases for all five cities. Resolve the Baku tour the owner shared and give each chapter direct marketplace or locally based guide links. Label unconfirmed dates and quote details, and keep budget changes in the visitor's hands. [Guide research](guided-research/RESEARCH.md)

## Creative direction

Keep this an editorial travel guide for general readers. Use Taste Skill v2 with design variance 7, motion intensity 4, and visual density 3 for discovery. Use intensity 2 and density 5 in the calculator and the comparison to keep changing numbers easy to follow. Use the native static app, local Bodoni and Manrope, and the existing forest-and-paper palette. Let photographic bands reach the viewport edges. Center the tools on shared rails with enough room for text and controls. Keep the narrow measure for reading.

Use Stageshow for the existing optional visual briefings and compare storyboard framing, intermediate transitions, compact layout, and reduced-motion posters. Keep any new motion tied to a visitor's action. Preserve system focus and document any capture gaps.

## Acceptance and order

1. Inventory, independent measured walkthroughs, copy index, and source review. Investigate overflow, intended alignment spreads over 1 px, targets under 44 px, 60–75 characters per full line of body/help text, and text that hides meaning when it wraps.
2. Rank each proposed change, link actual screenshots and annotated static mockups, and get a cold advisor review. Publish the owner review page and save an explicit decision for each id. The owner directed us to proceed with recommended items without a second wait. This instruction applies to the recorded recommendations.
3. Write failing checks in separate commits before approved changes. Scope lanes by source files. Capture every visible change in the UI change log. Stop and report after three failed implementation rounds against a single check.
4. Re-run the same measurements against the integrated build. Fix material findings and freeze the exact build. Run the full suite alone and get two independent fresh-browser reviews on the same source and output bytes. Both must cover online and offline, touch and keyboard, motion and reduced motion, all five chapters, and the real trip decisions. A material failure restarts the consecutive count.
5. Verify both live release bytes and the offline download, then close the goal. Track time, evidence, and open limitations.

## Improvement log

| Pass | Work | Evidence |
| --- | --- | --- |
| Baseline | Live and standalone outputs unchanged. Started read-only inventory, layout walkthroughs, and owner requirement traceability. | Baseline commit above. |
| Owner review | Published nine measured proposals and recorded eight approvals to proceed. Deferred the ultrawide and flat-map label study. | [Review page](https://meshthegreat.github.io/december-elsewhere/ui-review/) · [Decisions](review/decisions.json) |
| Build | Implemented the mobile improvements in isolated source lanes. Wrote and ran failing checks before source changes. | [Build record](IMPLEMENTATION.md) · [UI change log](UI-CHANGELOG.md) |
| Re-check | Corrected the two 320 px budget baselines and Stage note spacing. The first dry attempt then found 19 landscape photo states with clipped arrow controls. The corrected viewer passed its all-photo checks. Restarted the two-round count. | [First attempt and measurements](round-1/REPORT.md) |
| Re-check | Chrome cleared the photo fix. Edge found obscured keyboard focus after changing a landscape preview scene. Added failing checks, then placed Close beside the landscape stage and closed the panel on a mount failure. Restarted the two-round count on the new frozen candidate. | [Chrome result](round-2/REPORT.md) · [Edge finding](round-3/REPORT.md) · [Corrected landscape measurement](measure/landscape-preview-final.json) |
| Final dry rounds | Two independent browsers passed the exact combined candidate after the guided outing choices were added. Each review covered both delivery formats. | [Chrome review](final-chrome/REPORT.md) · [Edge review](final-edge/REPORT.md) |
| Release | The sequential suite passed all ten checks. GitHub Pages served the reviewed files byte for byte. The public browser checks and throttled phone measurements ran against that deployment. | [Release evidence and remaining limitations](RELEASE.md) |
