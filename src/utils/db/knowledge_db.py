from src.utils.db.main import DBConnect


class KnowledgeDB(DBConnect):
    def __init__(self, DB_NAME, COLLECTION_NAME):
        super().__init__(
            DB_NAME=DB_NAME,
            COLLECTION_NAME=COLLECTION_NAME
        )
        self.category = self.client[DB_NAME]['category']

    def update(self, query, data):
        self.db.update_one(query, {'$set': data}, upsert=True)

    def update_category(self, query, data):
        self.category.update_one(query, {'$set': data}, upsert=True)

    def delete(self, query):
        self.db.update_many(query, {'$set': {'is_deleted': True}})
        self.category.update_many(query, {'$set': {'is_deleted': True}})

    def query_category(self, text, provider='local'):
        from src.config import VIET_CHUNKER
        embedding = VIET_CHUNKER.embed([text], type='query', provider=provider)[0].tolist()
        query = [
            {
                '$vectorSearch': {
                    'index': 'embeddings_vector_search',
                    'path': 'embedding',
                    'filter': {
                        'is_deleted': {'$ne': True},
                        'provider': provider
                    },
                    'queryVector': embedding,
                    'numCandidates': 20,
                    'limit': 20,
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'docGuid': 1,
                    'subject': 1,
                    'summary': 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            },
            {
                '$match': {
                    'score': {'$gte': 0.6}
                }
            },
            {
                '$sort': {'score': -1}
            }
        ]
        res = self.category.aggregate(query)
        res = list(res)
        return res, embedding

    def query(self, text, provider='local', top=10, threshold=0.6):
        categories, embedding = self.query_category(text, provider)
        filter = {
            'is_deleted': {'$ne': True},
            'provider': provider,
        }
        if len(categories) > 0:
            filter['docGuid'] = {'$in': [category['docGuid'] for category in categories]}
        query = [
            {
                '$vectorSearch': {
                    'index': 'embeddings_vector_search',
                    'path': 'embedding',
                    'filter': filter,
                    'queryVector': embedding,
                    'numCandidates': top * 2,
                    'limit': top,
                }
            },
            {
                '$project': {
                    'docGuid': 1,
                    'chunkGuid': 1,
                    'subject': 1,
                    'summary': 1,
                    'content': 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            },
            {
                '$match': {
                    'score': {'$gte': threshold}
                }
            },
            {
                '$sort': {'score': -1}
            }
        ]
        res = self.query_agg(query)
        return res

    def get_list_category(self, subject):
        match = {
            'is_deleted': {'$ne': True},
        }
        if subject:
            match['subject'] = {'$regex': subject, '$options': 'i'}
        query = [
            {
                '$match': match
            },
            {
                '$project': {
                    '_id': 0,
                    'docGuid': 1,
                    'subject': 1,
                    'summary': 1
                }
            }
        ]
        res = self.category.aggregate(query)
        res = list(res)
        return res
