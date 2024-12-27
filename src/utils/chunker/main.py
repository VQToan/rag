import os
import re

import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer

path_model = os.path.join(os.path.dirname(__file__), 'all-MiniLM-L6-v2.onnx')


def mean_pooling(token_embeddings, attention_mask):
    input_mask_expanded = np.expand_dims(attention_mask, -1).astype(np.float32)
    sum_embeddings = np.sum(token_embeddings * input_mask_expanded, axis=1)
    sum_mask = np.clip(input_mask_expanded.sum(1), a_min=1e-9, a_max=None)
    return sum_embeddings / sum_mask


class ModelEmbedding:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.session = ort.InferenceSession(path_model)

    def encode(self, texts, type=None):
        encoded_input = self.tokenizer(texts, padding=True, truncation=True, return_tensors='np')
        model_output = self.session.run(None, {
            'input_ids': encoded_input['input_ids'],
            'attention_mask': encoded_input['attention_mask']
        })
        sentence_embeddings = mean_pooling(model_output[0], encoded_input['attention_mask'])
        sentence_embeddings = sentence_embeddings / np.linalg.norm(sentence_embeddings, axis=1, keepdims=True)
        return sentence_embeddings


class LLMEmbedding:
    def __init__(self):
        pass

    def encode(self, texts, type):
        from src.utils.gemini import GeminiEmbedding
        if type == 'doc':
            embeddings = GeminiEmbedding(texts, type='RETRIEVAL_DOCUMENT', dim=384)
        else:
            embeddings = GeminiEmbedding(texts, type='RETRIEVAL_QUERY', dim=384)
        return np.array(embeddings)


class VietnameseChunker:
    def __init__(self, chunk_size=300):
        self.model = LLMEmbedding()
        self.chunk_size = chunk_size

    def chunk(self, text):
        sentences = self.split_into_sentences(text)
        if not sentences:
            return []

        embeddings = self.model.encode(sentences, type='doc')

        chunks = []
        start = 0
        current_chunk = []
        current_length = 0

        while start < len(sentences):
            current_chunk.append(sentences[start])
            current_length += len(sentences[start].split())

            if current_length >= self.chunk_size or start == len(sentences) - 1:
                if current_length > self.chunk_size and len(current_chunk) > 1:
                    best_end = self.find_best_boundary(embeddings[start - len(current_chunk) + 1:start + 1])
                    chunks.append(' '.join(current_chunk[:best_end]))
                    start = start - len(current_chunk) + best_end
                    current_chunk = []
                    current_length = 0

            start += 1

        if len(current_chunk) > 0:
            chunks.append(' '.join(current_chunk))

        return chunks

    def find_best_boundary(self, embeddings, threshold=0.7):
        if len(embeddings) <= 1:
            return 1

        similarities = np.dot(embeddings[0], embeddings[1:].T) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1:], axis=1)
        )

        for i, similarity in enumerate(similarities):
            if similarity < threshold:
                return i + 1

        return len(embeddings)  # Trả về độ dài nếu không tìm thấy ranh giới rõ ràng

    def split_into_sentences(self, text):
        # Cải thiện phương pháp chia câu cho tiếng Việt
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def embed(self, texts, **kwargs):
        type = kwargs.get('type', None)
        return self.model.encode(texts, type=type)
