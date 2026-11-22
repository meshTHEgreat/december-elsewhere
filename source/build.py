"""Bundle the travel guide into one static HTML file. Uses only Python's standard library."""
import base64
import json
import mimetypes
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
load = lambda file: json.loads((ROOT / file).read_text(encoding="utf-8"))
cities = load("source/travel-data.json")
maps = load("source/travel-maps.json")
manifest = load("source/photography.json")
photos = {}
for entry in manifest:
    local = ROOT / "assets" / entry["file"]
    mime = "image/webp" if local.suffix.lower() == ".webp" else mimetypes.guess_type(local)[0] or "image/jpeg"
    entry = dict(entry, data=f"data:{mime};base64," + base64.b64encode(local.read_bytes()).decode())
    photos.setdefault(entry["city"], []).append(entry)
raw = json.dumps({"cities":cities,"maps":maps,"photos":photos}, ensure_ascii=False, separators=(",",":")).replace("<", "\\u003c")
template = (SOURCE / "index.template").read_text(encoding="utf-8")
parts = {
    "DATA": raw,
    "STYLE": (SOURCE / "styles.css").read_text(encoding="utf-8"),
    "SCRIPT": (SOURCE / "app.js").read_text(encoding="utf-8"),
}
for key, value in parts.items():
    template = template.replace(f"__{key}__", value)
(ROOT / "index.html").write_bytes(template.encode("utf-8"))
