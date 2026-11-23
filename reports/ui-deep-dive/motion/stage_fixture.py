"""Frame the exact vendored stage at the top of a local page for Stageshow film."""
import argparse
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def make_fixture(site_root, output):
    page = (site_root / "index.html").read_text(encoding="utf-8")
    styles = re.search(r"<style>(.*?)</style>", page, re.S).group(1)
    styles = styles.replace("url(\"media/", "url(\"/docs/media/")
    book = json.loads(re.search(r'<script type="application/json" id="dataset">(.*?)</script>', page, re.S).group(1))
    for mode in ("baku", "overview"):
        regional = mode == "baku"
        rows = (
            [(book["cities"][0], option) for option in book["winter"]["baku"]["options"]]
            if regional else [(city, book["winter"][city["id"]]["options"][0]) for city in book["cities"]]
        )
        frames = []
        for city, option in rows:
            chosen = option.get("filmPhoto", option["photo"])
            photo = next(photo for photo in book["photos"][city["id"]] if photo["file"] == chosen)
            frames.append({"title": option["title"] if regional else city["city"], "area": option["area"],
                           "note": option["filmNote"], "src": "/docs/" + photo["data"]})
        payload = json.dumps({"label": "Caspian to Caucasus" if regional else "Winter across the five", "frames": frames})
        fixture = f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>December, Elsewhere briefing rehearsal</title><link rel="icon" href="data:,">
<style>{styles} #example {{ width: min(736px, calc(100% - 32px)); margin: 20px auto; }}</style>
<div id="example"></div><script src="/docs/media/winter-stage.js"></script>
<script>DecemberWinterStage.mount(document.getElementById("example"),{payload})</script></html>"""
        output.mkdir(parents=True, exist_ok=True)
        (output / f"{mode}.html").write_text(fixture, encoding="utf-8")


if __name__ == "__main__":
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("output", type=Path)
    args.add_argument("--docs", type=Path, default=REPO / "docs")
    parsed = args.parse_args()
    make_fixture(parsed.docs, parsed.output)
