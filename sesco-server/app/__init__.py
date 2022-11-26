"""
Application Factory Module
"""
import json
from datetime import datetime
from config import config
from flask import Flask, current_app, g
from flask.json import JSONEncoder
from bson.objectid import ObjectId
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app import api
from controller.s3 import S3Controller
from model import register_connection_pool
from app.api.template import template as template_bp
from app.api.error_handler import error_handler as error_bp
from app.api.v1 import api_v1 as api_v1_bp
from app.api.auth import api_auth as api_auth_bp
from app.api.admin import api_admin as api_admin_bp


jwt_manager = JWTManager()
cors = CORS()


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%m:%S")
        elif isinstance(obj, ObjectId):
            return str(obj)
        else:
            return super().default(obj)


def create_sesco_app(config):
    app = Flask(import_name=__name__)

    app.json_encoder = CustomJSONEncoder
    app.config.from_object(config)
    config.init_app(app)
    api.init_app(app)
    jwt_manager.init_app(app)
    cors.init_app(app)
    register_connection_pool(app)
    # Init s3 controller
    app.s3 = S3Controller(
        aws_access_key_id=config.S3_ACCESS_KEY_ID,
        aws_secret_access_key=config.S3_SECRET_ACCESS_KEY,
        bucket_name=config.S3_BUCKET_NAME,
        bucket_domain=config.S3_DOMAIN,
    )
    

    app.register_blueprint(error_bp)
    app.register_blueprint(template_bp)
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
    app.register_blueprint(api_auth_bp, url_prefix='/api/auth')
    app.register_blueprint(api_admin_bp, url_prefix='/api/admin')

    return app