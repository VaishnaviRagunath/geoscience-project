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
    "translator",
    "dictionary",
    "translation",
    "subscribe",
    "privacy",
    "accessibility",
    "contact",
    "login",
    "newsletter"
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


# Only allow geoscience related topics
geoscience_keywords = [
    "geology",
    "earth",
    "earthquake",
    "tectonic",
    "volcano",
    "plate",
    "crust",
    "mantle",
    "core",
    "rock",
    "mineral",
    "sediment",
    "erosion",
    "climate",
    "atmosphere",
    "weather",
    "ocean",
    "hydrology",
    "groundwater",
    "glacier",
    "landslide",
    "soil",
    "geomagnetic",
    "geophysics",
    "geochemistry"
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

    # Keep only geoscience content
    if not any(word in content_lower for word in geoscience_keywords):
        continue

    # Remove template phrases
    for phrase in bad_phrases:
        content = content.replace(phrase, "")

    # Clean formatting
    cleaned_content = clean_text(content)

    # Skip very small content
    if len(cleaned_content) < 300:
        continue

    cleaned_doc = {
        "title": title,
        "content": cleaned_content,
        "source_url": url
    }

    clean_collection.insert_one(cleaned_doc)

    print("Cleaned:", title)


print("Cleaning completed")