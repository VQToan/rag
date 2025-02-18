import uuid

from flask import request

from src.config import VIET_CHUNKER, KNOWLEDGE_DB
from src.utils import GeminiClient


def add_knowledge_all():
    """
    Add knowledge to the database
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
        200:
            description: Successfully added knowledge to the database
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
                            errorMessages:
                                type: array
                                items:
                                    type: object
                                    properties:
                                        errorCode:
                                            type: string
                                            example: "Error"
                                        errorMessage:
                                            type: string
                                            example: "Please provide all the required fields : subject, content"
    """
    try:
        subject, summary, content, _ = validate()
        list_provider = ['local', 'gemini', 'openai']
        result = {}
        for provider in list_provider:
            result[provider] = add_knowledge_func(subject, summary, content, provider)
        return {
            'isOK': True,
            'result': result
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


def add_knowledge():
    """
    Add knowledge to the database
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
                        provider:
                            type: string
                            description: The provider of the knowledge
                            example: "gemini"
    responses:
        200:
            description: Successfully added knowledge to the database
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
                            errorMessages:
                                type: array
                                items:
                                    type: object
                                    properties:
                                        errorCode:
                                            type: string
                                            example: "Error"
                                        errorMessage:
                                            type: string
                                            example: "Please provide all the required fields : subject, content"
    """
    try:
        subject, summary, content, provider = validate()
        return add_knowledge_func(subject, content, provider,summary=summary)
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
    Validate request
    ---
    """
    subject = request.json.get('subject', None)
    summary = request.json.get('summary', None)
    content = request.json.get('content', None)
    provider = request.json.get('provider', None)
    if subject is None or content is None:
        raise Exception('Please provide all the required fields : subject, content')
    if subject == '' or content == '':
        raise Exception('Please provide all the required fields : subject, content')
    return subject, summary, content, provider


def chunk_text(text, provider='gemini'):
    """
    Chunk text into smaller parts
    ---
    """
    return VIET_CHUNKER.chunk(text, provider)


def embedding_text(texts, provider='gemini'):
    """
    Embed text
    ---
    """
    return VIET_CHUNKER.embed(texts, type='doc', provider=provider)


def summarize_text(text):
    """
    Summarize text
    ---
    """
    prompt = """Bạn là trợ lý được giao nhiệm vụ tóm tắt tài liệu để truy xuất. Các bản tóm tắt này sẽ được nhúng và sử dụng để truy xuất phần tử văn bản. Đưa ra bản tóm tắt ngắn gọn (**only 100 words**) về văn bản được tối ưu hóa tốt để truy xuất."""
    text = f"{prompt}\n. Dưới đây là tài liệu cần tóm tắt:\n{text}"
    client = GeminiClient()
    return client(text)


def add_knowledge_func(subject, content, provider, summary=None, doc_guid=str(uuid.uuid4())):
    """
    Add knowledge to the database
    ---
    """
    if summary == '' or summary is None:
        summary = summarize_text(content)
    KNOWLEDGE_DB.update_category(
        {'docGuid': doc_guid},
        {
            'subject': subject,
            'summary': summary,
            'provider': provider,
            'embedding': VIET_CHUNKER.embed([summary], type='doc', provider=provider)[0].tolist()
        })
    chunks = chunk_text(content)
    embeddings = embedding_text(chunks)
    chunks_guid = []
    for chunks, embeddings in zip(chunks, embeddings):
        chunk_guid = str(uuid.uuid4())
        KNOWLEDGE_DB.update(
            query={
                'docGuid': doc_guid,
                'chunkGuid': chunk_guid
            },
            data={
                'docGuid': doc_guid,
                'chunkGuid': chunk_guid,
                'provider': provider,
                'subject': subject,
                'summary': summary,
                'content': chunks,
                'embedding': embeddings.tolist()
            }
        )
        chunks_guid.append(chunk_guid)
    return {
        'isOK': True,
        'result': {
            'docGuid': doc_guid,
            'chunksGuid': chunks_guid
        }
    }
