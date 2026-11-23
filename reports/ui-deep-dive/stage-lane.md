# UI-06 | Winter preview lane

**Done.** Both optional Stageshow sequences still play once. The short landscape artboard is 460 × 190 CSS px with 14 px body text, compared with the previous 365 px high compact artboard. At 667 × 375 the shared sticky controls end at y103.6. Focused Close occupies y121.7–165.7, and all of the artboard fits from y173.7 to y363.7. The three Baku scenes and all five city scenes fit above their progress line.

Close comes first in the preview, so Tab advances to its named scene buttons. Enter on a scene stops the automatic sequence and holds the selected frame. Reduced-motion readers can choose any scene as a still. Escape or Close returns visible keyboard focus to the opener. Rotating to portrait preserves a selected frame. Both original scripts, photos and factual notes remain.

## Copy and owner request

| Copy | Approved text |
| --- | --- |
| C18 | Winter previews |
| C19 | Loading preview |
| C20 | Preview unavailable. Read the winter plans above. |

The owner asked for actual Stageshow and a phone-first result. Keep both locally packaged previews, their accessible guide text, and lower-priority controls reachable in normal document order. No other proposal belongs to this lane.

## Commits and checks

| Commit | Work |
| --- | --- |
| `527e427` | Failing tests on the baseline for focus, viewport fit, scene selection, autonomous playback and CSS rules. |
| `52ef648` | Actual Stageshow preview and chooser implementation, with rebuilt vendor files. |
| `9a47c96` | Separate red check for every scene's body text against the landscape progress rail. |
| `a120354` | Shallow-only paragraph margin reset leaves room for all notes. |

The lane rendered with the integration branch's approved outer panel scroll margin and Close spacing. All five checks in [verify_ui_stage.py](../../source/verify_ui_stage.py) passed in Chrome 157. [The existing winter verification](../../source/verify_winter.py) passed offline at 320, 390, 667 and 1440 with no HTTP requests or errors. An additional HTTP rehearsal delayed the runtime during a switch to the other preview, then blocked the runtime in a fresh browser. It confirmed the requested sequence survives the loading race and the failure text remains available. The landscape capture and portrait rotation were checked visually and with actual viewport geometry. Final integration film and dry-round checks run on the combined candidate.

The Stage bundle grew by 807 bytes raw and 297 bytes gzip. Its stylesheet grew by 670 bytes raw and 161 bytes gzip. The optional bundle still loads only on request.
