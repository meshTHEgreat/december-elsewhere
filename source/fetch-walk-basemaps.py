"""Refresh georeferenced Sentinel-2 walk imagery. Requires rasterio, numpy and Pillow."""
import json
import math
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import rasterio
from PIL import Image
from rasterio.transform import from_bounds
from rasterio.warp import Resampling, reproject


ROOT = Path(__file__).resolve().parents[1]
CATALOG = "https://earth-search.aws.element84.com/v1"
COLLECTION = "sentinel-2-l2a"
DATE_RANGE = "2025-05-01T00:00:00Z/2025-10-01T00:00:00Z"
MARGIN = 0.0004
MAP_SIZE = 600, 350


def viewport(anchor):
    """Match paintMap's projection and include the entire visible map rectangle."""
    points = [anchor["start"]]
    for route in anchor["routes"]:
        points.extend([route["point"], *route["path"]])
    south, north = min(p[0] for p in points), max(p[0] for p in points)
    west, east = min(p[1] for p in points), max(p[1] for p in points)
    cosine = math.cos(math.radians(anchor["start"][0]))
    scale = min(495 / max((east - west) * cosine, .0006), 270 / max(north - south, .0006))
    center_x, center_y = (west + east) / 2, (south + north) / 2
    return (center_x - 300 / scale / cosine, center_y - (MAP_SIZE[1] - 171) / scale,
            center_x + 300 / scale / cosine, center_y + 171 / scale)


def image_bbox(anchors):
    w, s, e, n = zip(*(viewport(anchor) for anchor in anchors))
    return min(w) - MARGIN, min(s) - MARGIN, max(e) + MARGIN, max(n) + MARGIN


def search(bounds):
    query = urlencode({
        "collections": COLLECTION,
        "datetime": DATE_RANGE,
        "bbox": ",".join(map(str, bounds)),
        "limit": 36,
        "query": json.dumps({"eo:cloud_cover": {"lt": 12}}),
        "sortby": "-properties.datetime",
    })
    url = f"{CATALOG}/search?{query}"
    with urlopen(Request(url, headers={"User-Agent": "DecemberElsewhere/3"}), timeout=35) as response:
        return json.load(response)["features"]


def raster_in_view(asset, bounds, width, height, mode, bands):
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", GDAL_HTTP_TIMEOUT="22"):
        with rasterio.open(asset) as data:
            result = np.zeros((len(bands), height, width), dtype=np.uint8)
            reproject(source=rasterio.band(data, bands), destination=result, src_nodata=0,
                      dst_transform=from_bounds(*bounds, width, height), dst_crs="EPSG:4326",
                      dst_nodata=0, resampling=mode)
            return result


def render_city(item):
    city, mapping = item
    bounds = image_bbox(mapping["anchors"])
    w, s, e, n = bounds
    # Roughly native Sentinel-2 resolution, with a cap on very wide extents.
    width = min(1120, max(320, round((e-w)*111000*math.cos(math.radians((s+n)/2))/10)))
    height = min(960, max(260, round((n-s)*111000/10)))
    for scene in search(bounds):
        sw, ss, se, sn = scene["bbox"]
        if not (sw <= w and ss <= s and se >= e and sn >= n):
            continue
        try:
            scl = raster_in_view(scene["assets"]["scl"]["href"], bounds, width//3, height//3, Resampling.nearest, (1,))[0]
            bad = np.isin(scl, (0, 1, 3, 8, 9, 10, 11)).mean()
            if bad > .025 or (scl == 0).any():
                continue
            rgb = raster_in_view(scene["assets"]["visual"]["href"], bounds, width, height, Resampling.bilinear, (1, 2, 3))
            if (rgb == 0).all(axis=0).mean() > .008:
                continue
        except (rasterio.errors.RasterioError, KeyError) as error:
            print(f"{city}: {scene['id']}: {error}", flush=True)
            continue
        file = f"walk-satellite-{city}.webp"
        Image.fromarray(np.moveaxis(rgb, 0, -1), mode="RGB").save(ROOT/"assets"/file, "WEBP", quality=80, method=6)
        meta = {"file": file, "bbox": bounds, "width": width, "height": height,
                "date": scene["properties"]["datetime"][:10], "item": scene["id"],
                "source": f"{CATALOG}/collections/{COLLECTION}/items/{scene['id']}",
                "license": "https://dataspace.copernicus.eu/terms-and-conditions"}
        print(f"{city}: {meta['date']} {width}×{height}, {bad:.1%} flagged pixels", flush=True)
        return city, meta
    raise RuntimeError(f"No suitably clear, complete scene for {city}")


if __name__ == "__main__":
    routes = json.loads((ROOT/"source"/"travel-maps.json").read_text(encoding="utf-8"))
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = dict(pool.map(render_city, routes.items()))
    (ROOT/"source"/"walk-basemaps.json").write_bytes((json.dumps(results, indent=2)+"\n").encode("utf-8"))
