from flask import request

from src.config import KNOWLEDGE_DB


def get_list_knowledge():
    """
    Get list of knowledge
    ---
    tags:
      - RAG
    parameters:
        - in: query
          name: subject
          schema:
            type: string
          required: false
          description: The subject of the knowledge
          example: "Subject"
    responses:
        200:
            description: Successfully get list of knowledge
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            isOK:
                                type: boolean
                                example: true
                            result:
                                type: object
                                properties:
                                    guidDoc:
                                        type: string
                                        description: The guidDoc of the knowledge
                                        example: "123456"
        400:
            description: Bad request - Missing subject or content
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            isOK:
                                type: boolean
                                example: false

    """
    subject = request.args.get('subject', None)
    result = KNOWLEDGE_DB.get_list_category(subject)
    return {
        'isOK': True,
        'result': result
    }, 200
