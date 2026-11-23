"""Build the self-contained owner review from the measured proposal set."""
import base64
from html import escape
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPORT = HERE.parent
REPO = REPORT.parents[1]
REVISION = "https://github.com/meshTHEgreat/december-elsewhere/blob/main/reports/ui-deep-dive/"


def img(path, alt):
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f'<img loading="lazy" decoding="async" alt="{escape(alt)}" src="data:image/jpeg;base64,{data}">'


spec = json.loads((REPORT / "proposals.json").read_text(encoding="utf-8"))
copy = json.loads((REPORT / "copy" / "03-copy.json").read_text(encoding="utf-8"))
wording = {item["proposalId"]: item for item in copy["entries"] if item.get("proposalId")}
verified = dict(zip(
    (f"UI-{number:02d}" for number in range(1, 9)),
    ("320-budget", "390-nav", "667-walk", "390-photo", "667-atlas", "667-winter", "390-stays", "390-compare"),
))
items = []
for change in spec["proposals"]:
    ident = change["id"]
    title = escape(change["title"])
    views = []
    for index, name in enumerate(change["shots"]):
        after = index == 1 and change["decision"] == "yes"
        label = "Proposed layout study" if after else "Measured baseline"
        views.append(f'<figure>{img(REPORT / name, label + " for " + title)}<figcaption>{label}</figcaption></figure>')
    shipped = REPORT / "measure" / "shots" / (verified.get(ident, "") + ".jpg")
    if shipped.exists():
        label = "Rendered implementation"
        views.append(f'<figure>{img(shipped, label + " for " + title)}<figcaption>{label}</figcaption></figure>')
    copy_rows = []
    for key in change.get("copy", []):
        row = wording[key]
        before, after = escape(row["text"]["en"]), escape(row["proposed"]["en"])
        copy_rows.append(f"<li><strong>{key}</strong> {before} → {after}</li>")
    copy_block = f'<details open><summary>Copy changes</summary><ul class="copy">{"".join(copy_rows)}</ul></details>' if copy_rows else ""
    overlay = HERE / "shots" / (ident + "-spec.jpg")
    spec_block = f'<details><summary>Measured mockup overlay</summary>{img(overlay, "Annotated mockup with rail and control measurements")}</details>' if overlay.exists() else ""
    radio = "".join(f'<label><input type="radio" name="{ident}" value="{label.lower()}">{label}</label>' for label in ("Yes", "No", "Later"))
    items.append(f"""<article class="item" id="{ident}">
<p class="caption">{ident} · {escape(change["page"])} · {change["severity"]} impact · {change["effort"]} effort</p>
<h3>{title}</h3>
<p>{escape(change["what"])}</p><p><strong>Proposed change</strong><br>{escape(change["fix"])}</p>
<div class="photos">{''.join(views)}</div>
{spec_block}
<details><summary>Source and prior decisions</summary><p>{escape(change["tech"])}</p><p>{escape(change["asked differently"])}</p></details>
{copy_block}
<form data-proposal="{ident}"><fieldset><legend>Decision for {ident}</legend><div class="decisions">{radio}</div>
<label>Optional note<textarea name="note" rows="2"></textarea></label></fieldset></form>
</article>""")
links = [
    ("Inventory", "inventory/01-inventory.md"), ("Chrome and atlas", "chrome/02-chrome.md"),
    ("Chapters", "chapters/02-chapters.md"), ("Budget and Sources", "planning/02-planning.md"),
    ("Full copy index", "copy/03-copy.json"), ("Code and CSS", "code/04-code.md"),
    ("Independent advisor", "advisor/05-advisor.md"), ("Proposal JSON", "proposals.json"),
    ("Decision record", "review/decisions.json"),
]
index = " · ".join(f'<a href="{REVISION}{url}">{label}</a>' for label, url in links)
content = f'<p class="index">{index}</p>' + "".join(items)
decisions = {
    "baseline": spec["baseline"], "source": "Owner instruction in this conversation to proceed with recommendations. Mobile first. Wider layouts are a bonus.",
    "decisions": {item["id"]: {"decision": item["decision"], "note": "Proceed as specified." if item["decision"] == "yes" else "Keep for a later pass."} for item in spec["proposals"]},
}
(HERE / "decisions.json").write_bytes((json.dumps(decisions, indent=2) + "\n").encode("utf-8"))
template = (HERE / "template.html").read_text(encoding="utf-8")
page = template.replace("__CONTENT__", content).replace("__DEFAULTS__", json.dumps(decisions).replace("<", "\\u003c"))
out = REPO / "docs" / "ui-review" / "index.html"
out.parent.mkdir(exist_ok=True)
out.write_bytes(page.encode("utf-8"))
