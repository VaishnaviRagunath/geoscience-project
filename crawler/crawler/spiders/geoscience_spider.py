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
        "earth",
        "geo",
        "rock",
        "mineral",
        "tectonic",
        "volcano",
        "earthquake",
        "climate",
        "atmosphere",
        "ocean",
        "erosion",
        "sediment",
        "soil",
        "hydrology",
        "glacier",
        "geology",
        "geophysics"
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