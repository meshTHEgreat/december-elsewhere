"""Generate the self-contained guide and the GitHub Pages build."""
import base64
import json
import mimetypes
from pathlib import Path
from shutil import copyfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
VENDOR = SOURCE / "vendor"
load = lambda file: json.loads((ROOT / file).read_text(encoding="utf-8"))
cities = load("source/travel-data.json")
maps = load("source/travel-maps.json")
manifest = load("source/photography.json")
editorial = load("source/editorial.json")
land = load("source/vendor/land.json")
winter = load("source/winter-data.json")
guided = load("source/guided-data.json")
outdoor = load("source/outdoor-stays.json")
basemaps = load("source/walk-basemaps.json")
template = (SOURCE / "index.template").read_text(encoding="utf-8")
sheet = "\n".join(path.read_text(encoding="utf-8") for path in
                  (SOURCE / "styles.css", SOURCE / "winter.css", SOURCE / "guided.css", VENDOR / "winter-stage.css"))
script = "\n".join((SOURCE / name).read_text(encoding="utf-8") for name in ("app.js", "winter.js", "guided.js", "atlas.js"))
fonts = ("bodoni", "bodoni-italic", "manrope")
licenses = ("THREE-LICENSE.txt", "BODONI-LICENSE.txt", "MANROPE-LICENSE.txt",
            "STAGESHOW-LICENSE.txt", "REACT-LICENSE.txt")


def data_uri(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def render(online):
    photos = {}
    for entry in manifest:
        name = entry["file"]
        local = ROOT / "assets" / name
        mime = "image/webp" if local.suffix.lower() == ".webp" else mimetypes.guess_type(local)[0] or "image/jpeg"
        src = f"media/{name}" if online else data_uri(local, mime)
        photos.setdefault(entry["city"], []).append(dict(entry, data=src))
    previews = {city: data_uri(ROOT / "assets" / "previews" / entry["cover"], "image/webp")
                for city, entry in editorial["cities"].items()}
    maps_with_images = {
        city: dict(entry, data=(f'media/{entry["file"]}' if online else data_uri(ROOT / "assets" / entry["file"], "image/webp")))
        for city, entry in basemaps.items()
    }
    raw = json.dumps({"cities": cities, "maps": maps, "editorial": editorial, "land": land,
                      "photos": photos, "previews": previews, "winter": winter, "outdoor": outdoor,
                      "basemaps": maps_with_images, "guided": guided},
                     ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    styles = sheet
    for font in fonts:
        asset = VENDOR / f"{font}.woff2"
        src = f"media/{asset.name}" if online else data_uri(asset, "font/woff2")
        styles = styles.replace(f"__{font}__", src)
    parts = {
        "DATA": raw,
        "STYLE": styles,
        "COVER": next(photo["data"] for photo in photos["prague"] if photo["file"] == "prague-detail.webp"),
        "GLOBE": "" if online else encode_script("globe.js"),
        "GLOBE_ATTR": ' data-src="media/globe.js"' if online else "",
        "WINTER_STAGE": "" if online else encode_script("winter-stage.js"),
        "WINTER_ATTR": ' data-src="media/winter-stage.js"' if online else "",
        "NOTICES": "\n\n".join((VENDOR / name).read_text(encoding="utf-8") for name in licenses),
        "SCRIPT": script,
        "SELF": "'self' " if online else "",
        "OFFLINE_LINK": '<a href="offline.html" download>Download offline guide ↓</a>' if online else "",
    }
    page = template
    for key, value in parts.items():
        page = page.replace(f"__{key}__", value)
    return page.encode("utf-8")


def encode_script(name):
    return json.dumps((VENDOR / name).read_text(encoding="utf-8"), ensure_ascii=False).replace("<", "\\u003c")


standalone = render(online=False)
(ROOT / "index.html").write_bytes(standalone)
pages = ROOT / "docs"
media = pages / "media"
media.mkdir(parents=True, exist_ok=True)
(pages / ".nojekyll").touch()
(pages / "index.html").write_bytes(render(online=True))
(pages / "offline.html").write_bytes(standalone)
for entry in manifest:
    name = entry["file"]
    copyfile(ROOT / "assets" / name, media / name)
for entry in basemaps.values():
    name = entry["file"]
    copyfile(ROOT / "assets" / name, media / name)
for name in (*[f"{font}.woff2" for font in fonts], "globe.js", "winter-stage.js", *licenses):
    copyfile(VENDOR / name, media / name)
