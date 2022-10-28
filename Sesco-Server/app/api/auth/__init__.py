"""
Auth API Module Package
"""
from flask import Blueprint
from config import FLASK_CONFIG


api_auth = Blueprint('api_auth', __name__)

from . import base
# production 모드에 한하여, Oauth API 활성화
if FLASK_CONFIG == 'production':
    from . import kakao
