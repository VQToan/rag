import json
import os

from dotenv import load_dotenv

from src.utils import Logger, VietnameseChunker
from src.utils.db import KnowledgeDB

load_dotenv()
WORKDIR = os.getcwd()

# ============================================
# Swagger Configurations
# ============================================
SWAGGER = {
    "specs_route": "/swagger/",
    "openapi": "3.0.2",
}

# ============================================
# Elastic APM Configurations
# ============================================
ELASTIC_APM = {
    'SERVICE_NAME': 'RAG',
    'SERVER_URL': os.getenv('ELASTIC_APM_SERVER_URL'),
    'SECRET_TOKEN': '',
    'ENVIRONMENT': os.getenv('ELASTIC_APM_ENV'),
}

# ==============================================
# Logger Configurations
# ==============================================
logger_init = Logger()
logger = logger_init()

# ==============================================
# Load Vietnamese Chunker
# ==============================================
VIET_CHUNKER = VietnameseChunker(chunk_size=300)

# ==============================================
# MongoDB Configurations
# ==============================================
KNOWLEDGE_DB = KnowledgeDB(
    DB_NAME=os.getenv('KNOWLEDGE_DB_NAME'),
    COLLECTION_NAME=os.getenv('KNOWLEDGE_COLLECTION_NAME')
)

# ==============================================
# Tools Configurations
# ==============================================
with open(os.path.join(WORKDIR, 'src/utils/tools/function_call.json'), encoding='utf8') as json_file:
    TOOLS = json.load(json_file)
