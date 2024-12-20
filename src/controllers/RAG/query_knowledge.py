from flask import request

from src.config import logger, KNOWLEDGE_DB


def query_knowledge():
    """
    Query the knowledge from the database
    ---
    tags:
        - Knowledge
    parameters:
        - in: query
          name: top
          schema:
            type: integer
          description: The number of knowledge to be retrieved
          required: true
        - in: query
          name: retrieval_text
          schema:
            type: string
          description: The text to be retrieved
          required: true
        - in: query
          name: threshold
          schema:
            type: float
          description: The threshold of the knowledge to be retrieved
          required: true
    responses:
        200:
            description: Successfully get the knowledge from the database
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
                                    subject:
                                        type: string
                                        description: The subject of the knowledge
                                        example: "Subject"
                                    summary:
                                        type: string
                                        description: The summary of the knowledge
                                        example: "Summary"
                                    content:
                                        type: string
                                        description: The content of the knowledge
                                        example: "Content"
        400:
            description: Bad request - Missing retrieval_text
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            isOK:
                                type: boolean
                                example: false
        404:
            description: Knowledge not found
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            isOK:
                                type: boolean
                                example: false
                            errorMessages:
                                type: array
                                items:
                                    type: object
                                    properties:
                                        errorCode:
                                            type: string
                                            example: "KNOWLEDGE_NOT_FOUND"
                                        errorMessage:
                                            type: string
                                            example: "Knowledge not found"
    """
    try:
        top, retrieval_text, threshold = validate_request()
        response = KNOWLEDGE_DB.query(top, retrieval_text, threshold)
        return {
            'isOK': True,
            "result": response
        }, 200
    except Exception as e:
        logger.error(f"Error in query_knowledge: {e}")
        return {
            'isOK': False,
            'errorMessages': [
                {
                    'errorCode': 'Error',
                    'errorMessage': "An error occurred. Please try again."
                }
            ]
        }


def validate_request():
    """
    Validate the request
    """
    top = request.json.get('top', 10)
    retrieval_text = request.json.get('retrieval_text')
    threshold = request.json.get('threshold', 0.8)
    if retrieval_text is None or retrieval_text == '':
        raise Exception('Please provide all the required fields : retrieval_text')
    return top, retrieval_text, threshold
