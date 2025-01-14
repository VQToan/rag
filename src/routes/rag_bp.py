from flask import Blueprint, render_template

from src.controllers import add_knowledge, remove_knowledge, get_knowledge, get_list_knowledge, add_knowledge_all

rag_bp = Blueprint('rag_bp', __name__)


def welcome():
    return 'Welcome to RAG API'


def demo():
    return render_template('ui_test.html')


rag_bp.route('/')(welcome)
rag_bp.route('/liveness')(welcome)
rag_bp.route('/get', methods=['POST'])(get_knowledge)
rag_bp.route('/add', methods=['POST'])(add_knowledge)
rag_bp.route('/add_all', methods=['POST'])(add_knowledge_all)
rag_bp.route('/remove', methods=['DELETE'])(remove_knowledge)
rag_bp.route('/query', methods=['PUT'])(add_knowledge)
rag_bp.route('/list', methods=['GET'])(get_list_knowledge)
rag_bp.route('/demo', methods=['GET'])(demo)
