from flask import request

from src.config import KNOWLEDGE_DB
from src.utils import GeminiClient
from src.utils.openAI import OpenAIClient


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
                        retrieval_text:
                            type: string
                            description: The retrieval text
                            example: "Hello"
                        type:
                            type: string
                            description: The type of the knowledge
                            example: "gemini"
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
        retrieval_text, type_rag = validate()
        if type_rag == 'gemini':
            response = get_knowledge_by_gemini(retrieval_text)
        elif type_rag == 'openai':
            response = get_knowledge_by_openai(retrieval_text)
        elif type_rag == 'openai_only':
            response = get_knowledge_by_openai_no_rag(retrieval_text)
        else:
            response = 'Invalid'
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
    retrieval_text = request.json.get('retrieval_text')
    type_rag = request.json.get('type', 'gemini')
    if retrieval_text is None or retrieval_text == '':
        raise Exception('Please provide all the required fields : retrieval_text')
    return retrieval_text, type_rag


def get_knowledge_by_gemini(retrieval_text):
    knowledge = KNOWLEDGE_DB.query(retrieval_text, provider='gemini')
    knowledge_context = ''
    for idx, k in enumerate(knowledge):
        knowledge_context += f'#Chunk {idx + 1}:\n ##Document title: {k["summary"]}\n##Chunk content: {k["content"]}\n\n'
    prompt = (
            f'You are a chatbot. You should be able to answer questions and provide information to users.The answer should be relevant and shortest possible.\n'
            f'Knowledge queried is: \n'
            f'Q: ' + retrieval_text + '\n'
                                      f'A: {knowledge_context}'
    )
    client = GeminiClient(
        instruction=prompt,
    )
    response = client(retrieval_text)

    return response


def get_knowledge_by_openai(retrieval_text):
    knowledge = KNOWLEDGE_DB.query(retrieval_text, provider='openai')
    knowledge_context = ''
    for idx, k in enumerate(knowledge):
        knowledge_context += f'#Chunk {idx + 1}:\n ##Document title: {k["summary"]}\n##Chunk content: {k["content"]}\n\n'
    prompt = (
            f'You are a chatbot. You should be able to answer questions and provide information to users.The answer should be relevant and shortest possible.\n'
            f'Knowledge queried is: \n'
            f'Q: ' + retrieval_text + '\n'
                                      f'A: {knowledge_context}'
    )
    client = OpenAIClient(instruction=prompt)
    response = client(retrieval_text)
    return response


def get_knowledge_by_openai_no_rag(retrieval_text):
    client = OpenAIClient(
        instruction='',
    )
    response = client(retrieval_text)
    return response
