import atexit
import json

from apscheduler.schedulers.background import BackgroundScheduler
from elasticapm.contrib.flask import ElasticAPM
from flasgger import Swagger
from flask import Flask

from src.background_process.rabbit_mq_listener import process_rabbitmq_messages
from src.config import logger
from src.routes import rag_bp

# ============================================
# App
# ============================================
app = Flask(__name__)
app.config.from_object('src.config')

# ============================================
# Initialize APM with the Flask app
# ============================================
apm = ElasticAPM(app)

# ============================================
# Scheduler
# ============================================
scheduler = BackgroundScheduler()
scheduler.add_job(func=process_rabbitmq_messages,
                  trigger="interval",
                  seconds=3,  # Chạy mỗi 3 giây
                  max_instances=2,  # Cho phép tối đa 2 phiên bản chạy đồng thời
                  coalesce=True)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())
# ============================================
# Swagger
# ============================================
template = json.load(open('src/utils/swagger_template.json'))
swagger = Swagger(app, template=template)

# ============================================
# Register Blueprint
# ============================================
app.register_blueprint(rag_bp, url_prefix='/')


# ============================================
# Error Handler
# ============================================
# @app.errorhandler(404)
# def not_found(error):
#     return {'message': 'Not found'}, 404


@app.errorhandler(500)
def internal_error(error):
    return {'message': 'Internal server error'}, 500


@app.errorhandler(405)
def method_not_allowed(error):
    return {'message': 'Method not allowed'}, 405


@app.errorhandler(400)
def bad_request(error):
    logger.error(f"Error: {error}")
    return {'message': 'Bad request'}, 400


@app.errorhandler(401)
def unauthorized(error):
    return {'message': 'Unauthorized'}, 401


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = '*'
    header['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    header['Access-Control-Allow-Credentials'] = 'true'
    return response
