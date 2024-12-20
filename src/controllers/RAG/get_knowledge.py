from flask import request

from src.config import KNOWLEDGE_DB
from src.utils import GeminiClient


def get_knowledge():
    """
    Get the knowledge from the database
    ---
    tags:
      - RAG
    requestBody:
        required: true
        content:
            application/json:
                schema:
                    type: object
                    properties:
                        top:
                            type: integer
                            description: The number of the top knowledge
                            example: 10
                        retrieval_text:
                            type: string
                            description: The retrieval text
                            example: "Hello"
                        threshold:
                            type: number
                            description: The threshold of the knowledge
                            example: 0.8
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
                            errorMessages:
                                type: array
                                items:
                                    type: object
                                    properties:
                                        errorCode:
                                            type: string
                                            description: The error code
                                            example: "Error"
                                        errorMessage:
                                            type: string
                                            description: The error message
                                            example: "Please provide all the required fields : retrieval_text"
    """
    try:
        top, retrieval_text, threshold = validate()
        knowledge = KNOWLEDGE_DB.query(retrieval_text)
        knowledge_context = ''
        for idx, k in enumerate(knowledge):
            knowledge_context += f'#Chunk {idx + 1}:\n ##Summary: {k["summary"]}\n##Content: {k["content"]}\n\n'
        prompt = (
                f'You are a chatbot. You should be able to answer questions and provide information to users.The answer should be relevant and shortest possible.\n'
                f'Knowledge queried is: \n'
                f'Q: ' + retrieval_text + '\n'
                                          f'A: {knowledge_context}'
        )
        # Get the knowledge from the database
        client = GeminiClient(
            instruction=prompt,
        )
        response = client(retrieval_text)
        return {
            'isOK': True,
            'result': response
        }
    except Exception as e:
        return {
            'isOK': False,
            'errorMessages': [
                {
                    'errorCode': 'Error',
                    'errorMessage': f'{e}'
                }
            ]
        }, 400


def validate():
    """
    Validate the request
    """
    top = request.json.get('top', 10)
    retrieval_text = request.json.get('retrieval_text')
    threshold = request.json.get('threshold', 0.8)
    if retrieval_text is None or retrieval_text == '':
        raise Exception('Please provide all the required fields : retrieval_text')
    return top, retrieval_text, threshold
