"""
API Main Decorator
"""
import json
import inspect
from functools import wraps
from time import time
from flask import current_app, g, Response
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.api.response import bad_access_token, forbidden
from model.mongodb import User
from config import config


def timer(func):
    """API Timer"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        process_time = time()
        result = func(*args, **kwargs)
        g.process_time = time() - process_time
        if current_app.config['DEBUG']:
            if isinstance(result, Response):
                data = json.loads(result.get_data())
                data['process_time'] = g.process_time
                result.set_data(json.dumps(data))
            elif (
                isinstance(result, tuple)
                and isinstance(result[0], dict)
            ):
                result[0]['process_time'] = g.process_time
            elif isinstance(result, dict):
                result['process_time'] = g.process_time
        return result
    return wrapper


def login_required(func):
    """일반 유저 토큰 검증 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        try:
            user_oid = ObjectId(get_jwt_identity())
        except InvalidId:
            return bad_access_token
        user_model = User(current_app.db)
        if not user_oid or not user_model.get_password(user_oid):
            return bad_access_token
        g.user_oid = user_oid
        # TODO: 유저 최근 액세스 날짜 트래킹, 더 괜찮은거 없을까?
        # user_model.update_last_access_date(user_id)
        return func(*args, **kwargs)
    return wrapper


def admin_required(func):
    """어드민 토큰 검증 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity: str = get_jwt_identity()
        if not isinstance(identity, str):
            return bad_access_token
        if identity != config.ADMIN_ID:
            return forbidden("Who are you?")
        # TODO 모든 어드민 API 실행 로그 추적 필요
        return func(*args, **kwargs)
    return wrapper