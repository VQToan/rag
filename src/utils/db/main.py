import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


class DBConnect:
    def __init__(self, DB_NAME, COLLECTION_NAME, DB_URL=os.getenv('ATLAS_URL')):
        self.atlas_url = DB_URL
        self.client = MongoClient(self.atlas_url)
        self.db = self.client[DB_NAME][COLLECTION_NAME]

    def query_agg(self, pipeline):
        result = self.db.aggregate(pipeline)
        return list(result)
