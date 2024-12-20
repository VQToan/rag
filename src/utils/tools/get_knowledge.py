

def get_knowledge_func(payload, **kwargs):
    from src.config import KNOWLEDGE_DB
    retrieval_texts = payload.get('retrieval_texts', [])
    response = []
    for retrieval_text in retrieval_texts:
        result = KNOWLEDGE_DB.query(retrieval_text, 4)
        response.append(result)

    return response
