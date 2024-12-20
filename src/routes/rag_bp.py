from flask import Blueprint

from src.controllers import add_knowledge, remove_knowledge, get_knowledge

rag_bp = Blueprint('rag_bp', __name__)


def welcome():
    return 'Welcome to RAG API'


rag_bp.route('')(welcome)

rag_bp.route('/get_knowledge', methods=['GET'])(get_knowledge)
rag_bp.route('/add_knowledge', methods=['POST'])(add_knowledge)
rag_bp.route('/remove_knowledge', methods=['DELETE'])(remove_knowledge)
