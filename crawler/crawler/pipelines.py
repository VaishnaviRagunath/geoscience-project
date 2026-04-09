import pymongo


class MongoDBPipeline:

    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["geoscience_db"]
        self.collection = self.db["raw_geoscience_data"]

    def process_item(self, item, spider):

        data = dict(item)

        if data.get("content"):
            self.collection.insert_one(data)
            print("Inserted into MongoDB:", data["title"])

        return item