from pymongo import MongoClient
import re

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["geoscience_db"]

raw_collection = db["raw_geoscience_data"]
clean_collection = db["cleaned_geoscience_data"]


def clean_text(text):

    if not text:
        return ""

    # Remove Britannica editor message
    text = re.sub(
        r"our editors will review.*?article",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove newline characters
    text = re.sub(r'\n+', ' ', text)

    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)

    # Remove weird characters
    text = re.sub(r'[^\w\s.,()-]', '', text)

    return text.strip()


# Remove unwanted titles/pages
unwanted_keywords = [
    "translator", "dictionary", "translation",
    "subscribe", "privacy", "accessibility",
    "contact", "login", "newsletter"
]


# Remove useless template text
bad_phrases = [
    "our editors will review",
    "thank you for your feedback",
    "subscribe to our newsletter",
    "advertisement",
    "privacy policy",
    "terms of use",
    "all rights reserved"
]


# Geoscience keywords (combined + improved)
geoscience_keywords = [

    # Core Earth Science
    "earth", "geology", "earthscience", "geophysics", "geochemistry",
    "crust", "mantle", "core",
    "lithosphere", "asthenosphere", "mesosphere",

    # Rocks & Minerals
    "rock", "mineral", "mineralogy", "petrology", "lithology",
    "igneous", "sedimentary", "metamorphic",
    "magma", "lava",
    "silicate", "feldspar", "quartz",
    "basalt", "granite", "schist", "gneiss", "shale", "limestone",
    "breccia", "conglomerate",
    "crystal", "ore",

    # Plate Tectonics
    "plate", "tectonic", "tectonics",
    "subduction", "rift", "fault",
    "continental drift", "orogeny", "seafloor",

    # Surface Processes
    "erosion", "weathering", "sediment", "deposition",
    "soil", "landform",
    "fluvial", "aeolian", "alluvium",

    # Natural Hazards
    "earthquake", "volcano", "eruption",
    "tsunami", "landslide", "flood", "drought",
    "hazard", "disaster",
    "epicenter", "hypocenter", "seismicity",
    "seismic", "p-wave", "s-wave",

    # Stratigraphy & Earth History
    "stratigraphy", "unconformity",
    "fossil", "paleontology",
    "geologic time", "evolution",
    "holocene", "anthropocene",

    # Hydrology & Oceans
    "ocean", "sea", "marine",
    "hydrology", "hydrosphere",
    "groundwater", "aquifer", "river",
    "karst", "stalactite", "stalagmite",
    "current", "wave",

    # Cryosphere
    "glacier", "glaciation", "moraine",
    "ice", "permafrost", "cryosphere",

    # Atmosphere & Climate
    "climate", "atmosphere", "weather",
    "meteorology",
    "climate change", "global warming", "greenhouse",

    # Geophysics Concepts
    "geomagnetic", "gravity",
    "paleomagnetism", "isostasy",

    # Resources & Energy
    "petroleum", "oil", "gas", "coal",
    "mining", "fossil fuel",
    "geothermal", "renewable",

    # Remote Sensing & GIS
    "topography", "bathymetry", "geodesy",
    "remote sensing", "gis",
    "satellite", "mapping",

    # Earth System
    "biosphere", "hydrosphere",
    "carbon cycle",

    # Rock Properties
    "cleavage", "fracture", "hardness",

    # Advanced Terms
    "batholith", "laccolith",
    "isotope", "radiometric"
]


for doc in raw_collection.find():

    title = doc.get("title", "")
    content = doc.get("content", "")
    url = doc.get("source_url", "")

    title_lower = title.lower()
    content_lower = content.lower()

    # Skip unwanted pages
    if any(word in title_lower for word in unwanted_keywords):
        continue

    # Combine title + content for better filtering
    combined_text = title_lower + " " + content_lower

    # Keyword threshold filtering (IMPORTANT)
    keyword_count = sum(
        1 for word in geoscience_keywords
        if word in combined_text
    )

    if keyword_count < 2:
        continue

    # Remove template phrases
    for phrase in bad_phrases:
        content = content.replace(phrase, "")

    # Clean formatting
    cleaned_content = clean_text(content)

    # Skip very small content
    if len(cleaned_content) < 300:
        continue

    # Remove duplicates
    if clean_collection.find_one({"content": cleaned_content}):
        continue

    cleaned_doc = {
        "title": title,
        "content": cleaned_content,
        "source_url": url
    }

    clean_collection.insert_one(cleaned_doc)

    print("Cleaned:", title)


print("✅ Cleaning completed successfully")