from waitress import serve

from src.main import app


def run_app():
    return app

if __name__ == '__main__':
    serve(app, host='0.0.0.0',  port=5002, url_prefix='/api/v1/rag')