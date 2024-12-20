import uuid

from flask import request

from src.config import VIET_CHUNKER, KNOWLEDGE_DB
from src.utils import GeminiClient


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
        subject, summary, content = validate()
        doc_guid = str(uuid.uuid4())
        if summary is None:
            summary = summarize_text(content)
        KNOWLEDGE_DB.update_category(
            {'docGuid': doc_guid},
            {
                'subject': subject,
                'summary': summary,
                'embedding': VIET_CHUNKER.embed([content])[0].tolist()
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
    if subject is None or content is None:
        raise Exception('Please provide all the required fields : subject, content')
    if subject == '' or content == '':
        raise Exception('Please provide all the required fields : subject, content')
    return subject, summary, content


def chunk_text(text):
    """
    Chunk text into smaller parts
    ---
    """
    return VIET_CHUNKER.chunk(text)


def embedding_text(texts):
    """
    Embed text
    ---
    """
    return VIET_CHUNKER.embed(texts)


def summarize_text(text):
    """
    Summarize text
    ---
    """
    prompt = """Bạn là trợ lý được giao nhiệm vụ tóm tắt tài liệu để truy xuất. Các bản tóm tắt này sẽ được nhúng và sử dụng để truy xuất phần tử văn bản. Đưa ra bản tóm tắt ngắn gọn về văn bản được tối ưu hóa tốt để truy xuất."""
    text = f"{prompt}\n. Dưới đây là tài liệu cần tóm tắt:\n{text}"
    client = GeminiClient()
    return client(text)
