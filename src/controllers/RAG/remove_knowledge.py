from flask import request

from src.config import KNOWLEDGE_DB


def remove_knowledge():
    """
    Remove the knowledge from the database
    ---
    tags:
      - RAG
    parameters:
        - name: docGuid
          in: query
          type: string
          required: true
          description: The unique identifier of the knowledge
    responses:
        200:
            description: Successfully removed knowledge from the database
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            isOK:
                                type: boolean
                                example: true
        400:
            description: Bad request - Missing docGuid
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            isOK:
                                type: boolean
                                example: false
    """
    if 'docGuid' not in request.args:
        return {
            'isOK': False,
            'message': 'Missing docGuid'
        }, 400
    doc_guid = request.args.get('docGuid')
    KNOWLEDGE_DB.delete({'docGuid': doc_guid})
    return {
        'isOK': True,
        'result': {
            'docGuid': doc_guid
        }
    }