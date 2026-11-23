"""Build the English traveler-facing copy index from the baseline guide sources."""
import json
import subprocess
from functools import cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASELINE = "6f017c54f0a6ad67ec4db8ab53d2cff767caf361"
COPY = []
CHOICES = []

OWNER = {
    "product": ("Keep December, Elsewhere, all five cities, 5–12 December 2026, Medina, and three adults.",
                "../../GOAL.md"),
    "navigation": ("Keep useful direct chapter and section navigation, including Winter, on phones.",
                   "../../PREMIUM-EXPERIENCE.md"),
    "atlas": ("Keep the geographic globe and static fallback. Separate direct distance from actual flights.",
              "../../PREMIUM-EXPERIENCE.md"),
    "walk": ('“I want the path to be shown better with real satellite or terrain.” Keep satellite and diagram, '
             "public starting points, estimated walking times, and direct Google Maps and Apple Maps links.",
             "../../WINTER-FIELD-GUIDE.md"),
    "outdoor": ('“Also prefer stays with somesort of outdoor environment.” Keep private, shared, nearby and '
                "unconfirmed access distinct and keep original listing links.",
                "../../WINTER-FIELD-GUIDE.md"),
    "winter": ("Keep date-specific conditions, operator verification and both Stageshow presentations.",
               "../../WINTER-FIELD-GUIDE.md"),
    "images": ("Keep real photos, attribution, license details, and downloads. Use original listings for room photos.",
               "../../WINTER-FIELD-GUIDE.md"),
    "planning": ("Keep budget arithmetic, actual unit distinctions, ten priced stays, 37 itinerary days and printing.",
                 "../../PREMIUM-EXPERIENCE.md"),
    "sources": ("Keep source links, dating, provenance and factual limits visible and usable offline.",
                "../../WINTER-FIELD-GUIDE.md"),
}


@cache
def read(source):
    return subprocess.check_output(["git", "show", f"{BASELINE}:{source}"], cwd=ROOT).decode("utf-8")


def line(source, marker):
    content = read(source)
    index = content.find(marker)
    if index < 0:
        raise ValueError(f"{source}: no source marker {marker!r}")
    return content.count("\n", 0, index) + 1


def add(source, where, text, *, marker=None, pointer=None, proposal=None, problem=None, protect=None, kind="UI"):
    if text is None or text == "":
        return
    value = str(text)
    entry = {
        "source": source,
        "line": line(source, marker) if marker else None,
        "jsonPointer": pointer,
        "where": where,
        "kind": kind,
        "text": {"en": value},
        "problem": problem,
        "proposed": {"en": value if proposal is None else proposal},
        "decision": "keep exact factual" if kind == "research" and proposal is None else "keep",
        "ownerProtected": bool(protect),
        "protectedRequirement": protect,
    }
    if proposal is not None:
        entry["decision"] = "propose for owner review"
        entry["proposalId"] = f"C{len(CHOICES) + 1:02d}"
        entry["characters"] = {"before": len(value), "proposed": len(proposal)}
        CHOICES.append(entry["proposalId"])
    COPY.append(entry)


def strings(source, marker, where, values, protect=None, kind="UI"):
    for value in values:
        add(source, where, value, marker=marker, protect=protect, kind=kind)


def change(source, marker, where, text, proposal, problem, protect=None):
    add(source, where, text, marker=marker, proposal=proposal, problem=problem, protect=protect)


HTML = "source/index.template"
APP = "source/app.js"
ATLAS = "source/atlas.js"
WINTER = "source/winter.js"

strings(HTML, "<meta name=\"description\"", "Page metadata", [
    "Five December 2026 trips from Medina, with stays, walking routes, day plans and a practical budget for three.",
    "December, Elsewhere | Five winter trips from Medina",
], "product")
strings(HTML, 'class="mast"', "Global mast, wordmark, navigation and accessible names", [
    "December, Elsewhere", "December, Elsewhere home", "Guide", "Cities", "Winter", "Compare",
], "navigation")
strings(HTML, 'class="skip"', "Keyboard skip link", ["Skip to guide"])
strings(HTML, 'class="hero"', "Opening cover", [
    "A winter travel journal", "December, elsewhere.", "Baku, Tbilisi, Budapest, Vienna and Prague.",
    "5–12 December 2026 / From Medina / Three travelers", "Prague · Old Town Square",
], "product")
change(HTML, "Explore the destinations", "Cover button", "Explore the destinations", "Explore cities",
       "Longer than the mast label for the same destination list.", "navigation")
strings(HTML, 'id="destinations"', "Cities headline and map controls", [
    "The atlas", "Where to?", "View globe", "Read chapter", "Destination guide",
], "navigation")
change(HTML, "Five trips from Medina", "Cities estimate help",
       "Five trips from Medina, with estimated costs per adult.", "Five trips from Medina. Estimates are per adult.",
       "Uses a fragment and splits the explanation on small phones.", "planning")
change(HTML, "Preview on the atlas", "Atlas city selector", "Preview on the atlas", "City on map",
       "Uses the editorial term atlas inside a practical control.", "atlas")
change(HTML, "From MED", "Atlas route clarification",
       "From MED · Actual flight connections are in each chapter", "From Medina. See Arrival for flights.",
       "Unexplained airport code. The word ‘chapter’ sits alone on a third line at 320 px.", "atlas")
change(HTML, "Back to the atlas", "Footer return link", "Back to the atlas ↑", "All cities ↑",
       "Different words for the same city list.", "navigation")
strings(HTML, 'id="photo-dialog"', "Photo dialog accessible name", ["Destination photograph"], "images")
strings("source/build.py", '"OFFLINE_LINK":', "Hosted footer download", ["Download offline guide ↓"])

strings(ATLAS, "function paintAtlas", "Flat route map origin label", ["Medina"], "atlas")
strings("source/globe.js", "start.textContent", "3D globe origin airport code", ["MED"], "atlas")
strings(ATLAS, "function previewDestination", "Atlas distance and chapter button templates", [
    "{distance} km direct", "Read {city}",
], "atlas", "template")
strings(ATLAS, "function bootAtlas", "Atlas loading and mode labels", ["Loading globe", "View map"], "atlas")
change(ATLAS, "This browser is using the static atlas.", "No WebGL or globe load error",
       "This browser is using the static atlas.", "Globe unavailable. Use the map.",
       "Names the technology state without a next action.", "atlas")
change(ATLAS, "The globe was interrupted.", "Globe context loss",
       "The globe was interrupted. The map is still available.", "Globe stopped. You can still use the map.",
       "Passive opening and unnecessary words.", "atlas")
strings(APP, "const money =", "All prices", ["SAR {amount}"], "planning", "template")
strings(APP, "function paintPick", "City list rows", ["{city}", "{dates} · {city tag}", "{price per adult}"], "product", "template")
strings(APP, "function photoCredit", "Photo attribution and download", [
    "Photo source", "Download photo ↓", "{caption} · {author} · {photo source} · {license} · {modifications}",
], "images")
strings(APP, "function galleryControls", "Inline gallery and dialog controls", [
    "Previous photo", "{current} / {total}", "Next photo",
], "images")
strings(APP, "function paintGallery", "Photo open control accessible name", ["View photo full screen: {photo title}"], "images")
strings(APP, "function paintPhotoDialog", "Photo dialog header and close control", ["{city} photos", "Close"], "images")
strings(APP, "const chapterLinks", "Chapter navigation and compact menu", [
    "Arrival", "Stays", "Walks", "Winter", "Itinerary", "Budget", "Photos", "Destination sections", "All cities",
], "navigation")
change(APP, "<summary>In ", "Closed compact chapter menu", "In {city}", "Sections · {current section}",
       "No visible current position on the closed menu in any of 105 phone section cases.", "navigation")
strings(APP, "function paintCity", "Chapter cover and arrival", [
    "{country} · {dates}", "{city}", "{nights} nights", "{price} per adult", "{price} for three", "Arrival in {city}",
    "Flights from Medina", "Outbound", "Return", "Entry, weather and booking",
], "product")
change(APP, "Published schedules; checkout not verified", "Flight fallback note",
       "Published schedules; checkout not verified", "Published times. Check before booking.",
       "Abstract verification wording. Keep the fact that these are published times.", "sources")
strings(APP, "function paintCity", "Flight details fallback", [
    "Baggage depends on fare family; price at checkout.",
], "planning")
strings(APP, "function flightLeg", "Actual flight row", ["{date} · {carrier}", "{route}", "{timing} · Local times"], "planning", "template")
strings(APP, "function stayCard", "Stay name and factual details", [
    "Airbnb", "{bedrooms} bedrooms", "{beds} beds", "{bathrooms} bath", "Bathrooms: check listing", "{rating}/5",
    "{reviews} reviews", "Earlier Airbnb observation · 23 Nov 2026", "Location from listing",
    "Check sleeping layout and arrival arrangements with the listing host.",
], "planning")
change(APP, "Price to check", "Stay without a published price", "Price to check", "Check price",
       "The shorter phrase starts with what to do.", "planning")
change(APP, "Listing & photos", "External stay booking action", "Listing & photos", "Listing & photos",
       "Keep the compact wording. Put the link beside price, bed and outdoor details.", "images")
change(APP, "In your budget", "Selected stay button", "In your budget", "Stay selected",
       "Current text sounds like the stay is affordable. It means the stay is selected.", "planning")
change(APP, "Use in budget", "Unselected stay button", "Use in budget", "Use this stay",
       "The action selects the stay and updates both budget and public walking start.", "planning")
change(APP, "Two priced options for three adults", "Stays introduction",
       "Two priced options for three adults. Open each listing for its room gallery and check winter access to outdoor spaces.",
       "Two stays for three adults. Check room photos and winter outdoor access in each listing.",
       "Dense opening. Keeps the reason for opening the actual listings.", "outdoor")
strings(APP, "function paintCity", "Alternate stay disclosure", ["Other stays", "Check dates, beds and total"], "outdoor")
change(APP, "From the photo journal", "Neighborhood photo caption lead", "From the photo journal · {credit}", "{credit}",
       "Repeats a section name without changing the caption or the required credit.", "images")
strings(WINTER, "function stayOutdoor", "Outdoor status fallback", [
    "Outdoor space unverified", "Ask whether outdoor space is attached to the unit.",
], "outdoor")
strings(WINTER, "function outdoorShortlist", "Outdoor recommendations and uncertainty", [
    "For outdoor space", "Start with the options marked private. {outdoor types}.",
    "Start with {listing}. Ask about private access and seating.",
    "The priced stays have no confirmed private outdoor space. See the additional listing below.",
    "Rates and date availability unverified.", "Open real listing photos",
], "outdoor")

strings(APP, "function paintMap", "Walk section labels and directions", [
    "Walks and transport", "Walking from", "Choose a walk", "Selected walk", "A · {public start} → B · {destination}",
    "Walk from {public start} to {destination}", "N ↑", "{min} min · {km} km", "≈ {min} min · {km} km",
    "{route name} · {min} min", "{route name}", "{min} min · {km} km · estimate", "Walk time unavailable",
    "Time unavailable", "No route calculated", "Dotted lines connect public pins to the routed path.",
    "Google and Apple may choose a different path.", "Contains modified Copernicus Sentinel data {year}",
    "Scene {date}", "© OpenStreetMap contributors",
], "walk")
change(APP, "Offline estimate", "Selected walk duration qualifier", "Offline estimate", "Estimated walk",
       "Where the calculation is stored matters less than what the time represents.", "walk")
change(APP, "Offline routing could not be verified", "Walk data unavailable",
       "Offline routing could not be verified for this destination.", "No verified walks for this city.",
       "Technical term and passive wording.", "walk")
strings(APP, "const caveat", "Public starting point caveats and Stay to Walk links", [
    "District hub example. Travel from the apartment to this hub is unverified.",
    "Public starting point for the selected stay.", "City reference walk from a different starting point.",
    "No starting point was confirmed for the selected stay. These are city reference walks.",
    "See walks from the public starting point", "See city reference walks",
], "walk")
strings(APP, "function providerDirections", "External route directions", ["Open in Google Maps", "Apple Maps"], "walk")
strings(APP, "function walkModes", "Map background and accessible name", ["Map background", "Satellite", "Diagram"], "walk")
strings(APP, "function walkScale", "Walking map scale", ["1 km", "{distance} m"], "walk", "template")
strings(APP, "function paintCity", "Transport details below map", [
    "Getting around", "In the city", "Airport transfer", "Day trips", "Short car hire",
], "planning")

strings(WINTER, "function winterMarkup", "Winter options and film open/close", [
    "Winter options", "{city} · Winter field guide", "Caspian to Caucasus", "Winter across the five", "Close preview",
], "winter")
change(WINTER, "Visual briefings", "Stageshow heading and introduction",
       "Visual briefings / See the plan in motion / Short visual guides. The trip facts and links are available above.",
       "Winter previews",
       "Three text elements describe the same two choices. Titles and facts stay available.", "winter")
strings(WINTER, "function winterOptionMarkup", "Winter photo and source labels", [
    "View photo full screen: {photo title}", "Route outline", "Official links", "Sources checked {date}.",
], "winter")
change(WINTER, "Loading visual briefing", "Winter preview loading", "Loading visual briefing", "Loading preview",
       "Match the label above.", "winter")
change(WINTER, "The visual briefing could not load", "Winter preview error",
       "The visual briefing could not load. The guide above is ready.", "Preview unavailable. Read the winter plans above.",
       "Mixed terminology and indirect recovery.", "winter")
strings("source/winter-stage.tsx", 'aria-label="Story progress"', "Stageshow accessible marker", [
    "Story progress", "{scene title}", "{scene area}", "{scene note}",
], "winter")
strings(APP, "function dayMarkup", "Open or closed day and day details", [
    "{day} Dec", "{title}", "{time} · {stop name}", "{duration} · {mode} · {travel}", "Meals",
    "{estimated meal and activity cost} per adult for the day.", "Alternative",
], "planning")
strings(APP, "function paintCity", "Chapter section headings and ending", [
    "Where to stay", "Winter plans", "Day by day", "The photo journal", "The decision · {city}",
    "What to weigh", "Compare trips", "Next chapter · {city}",
], "navigation")
change(APP, "Open a day for the stops", "Itinerary help",
       "Open a day for the stops, transit, meals and a fallback. Times and daily costs are estimates.",
       "Open a day for stops, transport, meals and an alternative. Times and costs are estimates.",
       "Clarifies what expands in ordinary travel language.", "planning")

strings(APP, "const fieldLabels", "Budget field labels", [
    "Base airfare", "Baggage & seat fees", "Accommodation with fees", "Meals & drinks", "Airport & local transport",
    "Admissions & activities", "Driver, tours or rail excursions", "Entry fees & insurance", "Rental base",
    "Fuel", "Parking", "Rental insurance", "Road tolls", "Contingency",
], "planning")
change(APP, "function budgetField", "Budget unit for shared costs", "group", "For three",
       "Makes the calculation basis explicit and matches the comparison table.", "planning")
change(APP, "function budgetField", "Budget unit for individual costs", "each", "Per adult",
       "Makes the calculation basis explicit and matches comparisons and city totals.", "planning")
change(APP, "Group total", "Budget total", "Group total", "Total for three",
       "Names how many people the value covers.", "planning")
strings(APP, "function paintCity", "Budget introduction and commands", [
    "Budget", "Costs for the full trip, in SAR.", "Car rental costs", "Reset city budget", "Print itinerary",
], "planning")
strings(APP, "function paintTotal", "Live budget total and range feedback", [
    "{amount} per adult", "{amount} for three", "Above the preferred budget.", "Below the target range.",
    "Within the preferred range.", "Includes contingency.",
], "planning")
strings(APP, "function paintCompare", "Comparison pickers, table, and details", [
    "The shortlist", "Compare trips", "First city", "Second city", "Trip detail", "Dates", "Nights", "Outbound",
    "Return", "Entry", "Winter", "Flights, entry and winter weather",
], "planning")
change(APP, "Adjust a city’s budget", "Trip comparison introduction",
       "Adjust a city’s budget and see the difference side by side.", "Choose two cities. Edit budgets to update the estimates.",
       "Current text omits the first action and what updates.", "planning")
strings(APP, "const comparePrices", "Comparison summaries", [
    "Per adult", "For three", "Stay", "Meals per adult", "Local transport per adult", "Outdoor space",
], "planning")
strings(WINTER, "function compareBudgetBars", "Per-adult comparison chart", [
    "Estimated per adult", "Shaded band: SAR 4,000–6,000 per adult",
], "planning")

strings(APP, "function paintEvidence", "Source disclosures and dated planning context", [
    "Sources", "Stay prices were observed on 23 November 2026. Flight times follow published schedules. Confirm both before booking.",
    "{city} sources", "Earlier estimate for three: {amount}.", "Photography credits", "Routes, atlas and currency",
    "Retrieved pedestrian paths and separately labeled walking estimates are packaged offline.",
    "Estimated directions use straight-line distance × 1.37 and an assumed 3.6 km/h.",
    "Actual crossings, grades and weather may change the time.", "OpenStreetMap attribution", "Valhalla routing",
    "The atlas connects Medina airport to approximate city centers.", "Globe arcs and distances use a spherical great circle.",
    "The map shows straight bearings on its projection.", "For actual connections, see the chapter’s outbound and return legs.",
    "Natural Earth", "OurAirports (MED)",
    "The calculator sums SAR inputs directly; prior examples were rounded during the 23 November 2026 research.",
    "Saudi Central Bank FX reference", "provides the exchange-rate archive. No live FX conversion.",
], "sources")
change(APP, "const quickWalk", "Phone walk selector option",
       "{route name} · {min} min", "{route name}",
       "The Selected walk already gives the time. Eight options exceed the 250.4 px text area at 320 px with minutes. Two still need the wrapped title shown in the route summary.", "walk")


def load(name):
    return json.loads(read(f"source/{name}.json"))


def data(name, pointer, where, value, protect):
    add(f"source/{name}.json", where, value, pointer="/" + "/".join(map(str, pointer)),
        protect=protect, kind="research")


def fields(name, pointer, where, item, names, protect):
    for field in names.split():
        data(name, (*pointer, field), where, item.get(field), protect)


for city, item in load("editorial")["cities"].items():
    fields("editorial", ("cities", city), f"{city} city list, cover, arrival and final decision", item,
           "tag headline intro finish", "product")

for i, city in enumerate(load("travel-data")):
    label = city["city"]
    fields("travel-data", (i,), f"{label} chapter, arrival and comparison", city,
           "city country dates nights priorTotal entry winter light", "product")
    fields("travel-data", (i, "flights"), f"{label} arrival and comparison flight details", city["flights"],
           "out back status bags note", "planning")
    fields("travel-data", (i, "transport"), f"{label} transport notes in Walks", city["transport"],
           "city transfer day rental", "planning")
    for j, item in enumerate(city["flights"]["links"]):
        fields("travel-data", (i, "flights", "links", j), f"{label} arrival sources", item, "label name", "sources")
    for j, stay in enumerate(city["stays"]):
        fields("travel-data", (i, "stays", j), f"{label} stay option {j + 1}", stay,
               "name platform price status bedrooms beds bathrooms rating reviews area notes", "outdoor")
    for j, stay in enumerate(city.get("alternatives", [])):
        fields("travel-data", (i, "alternatives", j), f"{label} alternate stay {j + 1}", stay,
               "name label notes note status", "outdoor")
    for j, day in enumerate(city["days"]):
        fields("travel-data", (i, "days", j), f"{label} itinerary day {j + 1}", day,
               "date title meal cost backup", "planning")
        for k, stop in enumerate(day["stops"]):
            fields("travel-data", (i, "days", j, "stops", k), f"{label} itinerary day {j + 1}, stop {k + 1}", stop,
                   "time name duration mode travel note", "planning")
    for j, source in enumerate(city["sources"]):
        fields("travel-data", (i, "sources", j), f"{label} sources and dates", source,
               "label name status checked note", "sources")

for city, item in load("winter-data").items():
    if city == "checked":
        data("winter-data", ("checked",), "Winter time of source check", item, "sources")
        continue
    fields("winter-data", (city,), f"{city} winter overview", item, "title summary", "winter")
    for i, option in enumerate(item["options"]):
        path = (city, "options", i)
        title = f"{city} winter option {i + 1}, or Stageshow frame"
        fields("winter-data", path, title, option, "title tag area status journey time conditions check filmNote", "winter")
        for j, idea in enumerate(option["ideas"]):
            data("winter-data", (*path, "ideas", j), title, idea, "winter")
        for j, (link, _url) in enumerate(option["links"]):
            data("winter-data", (*path, "links", j, 0), f"{city} winter official sources", link, "sources")

outdoors = load("outdoor-stays")
for id_, item in outdoors["listings"].items():
    fields("outdoor-stays", ("listings", id_), f"Stay outdoor access, listing {id_}", item, "label note", "outdoor")
for city, item in outdoors["alternatives"].items():
    fields("outdoor-stays", ("alternatives", city), f"{city} outdoor stay alternative", item, "title note", "outdoor")
for i, photograph in enumerate(load("photography")):
    fields("photography", (i,), f"{photograph['city']} photo, caption, alt text and credits", photograph,
           "title caption author license modifications", "images")
for city, map_ in load("travel-maps").items():
    fields("travel-maps", (city,), f"{city} walking map attribution", map_, "attribution", "walk")
    for i, anchor in enumerate(map_["anchors"]):
        path = (city, "anchors", i)
        fields("travel-maps", path, f"{city} public walking start", anchor, "name note", "walk")
        for j, route in enumerate(anchor["routes"]):
            fields("travel-maps", (*path, "routes", j), f"{city} selected walk, chooser, map and route list", route,
                   "name min km", "walk")
for city, item in load("walk-basemaps").items():
    fields("walk-basemaps", (city,), f"{city} satellite scene date", item, "date", "sources")

glossary = {
    "Cities": "City chooser and destination list. Use ‘map’ on controls and ‘atlas’ for the geographic section.",
    "Arrival": "Published flight details for the trip. Airport codes can stay in flight schedules.",
    "Stays": "Apartment and lodging options. ‘Listing’ opens the property’s actual gallery or booking site.",
    "Walks": "Selected pedestrian route and transport information.",
    "Public starting point": "Routing starts from a named public location. Use modeled start and distance caveats where shown.",
    "Estimated walk": "A modeled walking time and distance. Keep minutes and kilometers attached to their numbers.",
    "Satellite and Diagram": "Two backgrounds for the same selected route. Google Maps and Apple Maps supply online directions.",
    "Winter": "Date-specific conditions and choices. A ‘preview’ is an optional Stageshow presentation.",
    "Itinerary": "Daily trip plan. An ‘alternative’ is the backup plan.",
    "Budget": "Trip costs in SAR. ‘Per adult’ is individual. ‘For three’ is one shared amount.",
    "Photos": "Real destination photography with source, photographer and license. Never call place imagery a specific rental photo.",
    "Compare": "Two trips and their current estimated costs side by side.",
    "Outdoor space": "Distinguish private, shared, public nearby and unverified access.",
    "Sources": "Original authorities, dated observations and methodology.",
}
result = {
    "baseline": BASELINE,
    "languages": [{"code": "en", "direction": "ltr"}],
    "scope": {
        "indexed": "Source-authored visible copy, accessibility names, fallback states, displayed data and formatted-value templates.",
        "outside": "Native browser/operating system validation and dialogs, external sites, SVG icon-only glyphs, internal data keys, IDs, URLs as link targets and coordinates.",
        "method": "Source text anchors and exact displayed dataset fields. Curated changes require the owner’s review of the wording or an applicable recorded recommendation.",
    },
    "glossary": glossary,
    "ownerRequirements": {key: {"sourceInstruction": row[0], "reference": row[1]} for key, row in OWNER.items()},
    "counts": {"entries": len(COPY), "proposed": len(CHOICES), "data": sum(x["kind"] == "research" for x in COPY)},
    "entries": COPY,
}
(HERE / "03-copy.json").write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
