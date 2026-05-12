import scrapy
from urllib.parse import urljoin
from pymongo import MongoClient


class GeoscienceSpider(scrapy.Spider):

    name = "geoscience"

    allowed_domains = [
        "britannica.com",
        "usgs.gov",
        "science.nasa.gov",
        "weather.gov",
        "bgs.ac.uk",
        "americangeosciences.org",
        "naturalhistory.si.edu"
    ]

    start_urls = [

        "https://www.britannica.com/science/Earth-sciences",
        "https://science.nasa.gov/earth-science/",
        "https://www.usgs.gov/science",
        "https://www.weather.gov/jetstream/",
        "https://www.bgs.ac.uk/discovering-geology/",
        "https://www.americangeosciences.org/",
        "https://naturalhistory.si.edu/research/geology"
    ]

    # geoscience filter
    geoscience_keywords = [

    # 🌍 Core Earth Science
    "earth", "geology", "earthscience", "geophysics", "geochemistry",
    "crust", "mantle", "core",
    "lithosphere", "asthenosphere", "mesosphere",

    # 🪨 Rocks & Minerals
    "rock", "mineral", "mineralogy", "petrology", "lithology",
    "igneous", "sedimentary", "metamorphic",
    "magma", "lava",
    "silicate", "feldspar", "quartz",
    "basalt", "granite", "schist", "gneiss", "shale", "limestone",
    "breccia", "conglomerate",
    "crystal", "ore",

    # 🌋 Plate Tectonics
    "plate", "tectonic", "tectonics",
    "subduction", "rift", "fault",
    "continental drift", "orogeny", "seafloor",

    # 🌊 Surface Processes
    "erosion", "weathering", "sediment", "deposition",
    "soil", "landform",
    "fluvial", "aeolian", "alluvium",

    # 🌪 Natural Hazards
    "earthquake", "volcano", "eruption",
    "tsunami", "landslide", "flood", "drought",
    "hazard", "disaster",
    "epicenter", "hypocenter", "seismicity",
    "seismic", "p-wave", "s-wave",

    # 🧬 Stratigraphy & Earth History
    "stratigraphy", "unconformity",
    "fossil", "paleontology",
    "geologic time", "evolution",
    "holocene", "anthropocene",

    # 💧 Hydrology & Oceans
    "ocean", "sea", "marine",
    "hydrology", "hydrosphere",
    "groundwater", "aquifer", "river",
    "karst", "stalactite", "stalagmite",
    "current", "wave",

    # ❄️ Cryosphere
    "glacier", "glaciation", "moraine",
    "ice", "permafrost", "cryosphere",

    # 🌤 Atmosphere & Climate
    "climate", "atmosphere", "weather",
    "meteorology",
    "climate change", "global warming", "greenhouse",

    # 🌐 Geophysics Concepts
    "geomagnetic", "gravity",
    "paleomagnetism", "isostasy",

    # ⛽ Resources & Energy
    "petroleum", "oil", "gas", "coal",
    "mining", "fossil fuel",
    "geothermal", "renewable",

    # 🛰 Remote Sensing & GIS
    "topography", "bathymetry", "geodesy",
    "remote sensing", "gis",
    "satellite", "mapping",

    # 🌱 Earth System
    "biosphere", "hydrosphere",
    "carbon cycle",

    # 🔬 Rock Properties
    "cleavage", "fracture", "hardness",

    # 🧠 Advanced Terms (bonus for better filtering)
    "batholith", "laccolith",
    "unconformity", "isotope", "radiometric"
]

    def __init__(self):

        client = MongoClient("mongodb://localhost:27017/")
        db = client["geoscience_db"]
        self.collection = db["raw_geoscience_data"]

    def parse(self, response):

        title = response.css("title::text").get()

        paragraphs = response.css("p::text").getall()

        content = " ".join(paragraphs)

        if content and len(content) > 300:

            self.collection.insert_one({
                "title": title,
                "content": content,
                "source_url": response.url
            })

            print("Stored:", title)

        # follow links
        for link in response.css("a::attr(href)").getall():

            absolute_url = urljoin(response.url, link)

            # follow only geoscience related links
            if any(word in absolute_url.lower() for word in self.geoscience_keywords):

                yield scrapy.Request(
                    absolute_url,
                    callback=self.parse
                )