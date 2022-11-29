"""
API Server Base Auth APIs
"""
from flask import current_app, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_validation_extended import Validator, Json, MinLen
from flask_jwt_extended import (
    get_jwt_identity, create_refresh_token, create_access_token, jwt_required
)
from app.api.response import response_200, bad_request, forbidden, no_content
from app.api.decorator import timer, login_required
from model.mongodb import User
from config import config
from . import api_auth as api
from datetime import timedelta
from config import Config
@api.post('/signin')
@Validator(bad_request)
@timer
def auth_signin_api(
    id=Json(str, rules=MinLen(5)),
    pw=Json(str, rules=MinLen(8))
):
    """로그인"""
    user = User(current_app.db).get_password_with_id(id)
    if not user or user['password'] is None:
         return bad_request("Authentication failed.")
    if not check_password_hash(user['password'], pw):
        return bad_request("Authentication failed.")
    user_oid = str(user['_id'])
    return response_200({
        'access_token': create_access_token(
            user_oid,
            expires_delta= timedelta(Config.JWT_ACCESS_TOKEN_EXPIRES)
        ),
        'refresh_token': create_refresh_token(
            user_oid,
            expires_delta= timedelta(Config.JWT_ACCESS_TOKEN_EXPIRES)
        )
    })


@api.post('/signup')
@Validator(bad_request)
@timer
def auth_signup_api(
    id=Json(str, rules=MinLen(5)),
    pw=Json(str, rules=MinLen(8)),
    name=Json(str, rules=MinLen(1), optional=True),
):
    """회원가입"""
    user_model = User(current_app.db)
    if (
        user_model.get_password_with_id(id)
        or id == config.ADMIN_ID
    ):
        return bad_request('user_id already exists.')
    user_oid = user_model.insert_user({
        'id': id,
        'password': generate_password_hash(pw),
        'name':name if name else id
    }).inserted_id

    user_oid = str(user_oid)
    return response_200({
        'access_token': create_access_token(
            user_oid,
        expires_delta= timedelta(Config.JWT_ACCESS_TOKEN_EXPIRES)
        ),
        'refresh_token': create_refresh_token(
            user_oid,
            expires_delta= timedelta(Config.JWT_ACCESS_TOKEN_EXPIRES)
        )
    })


@api.get('/refresh')
@jwt_required(refresh=True)
def auth_token_refresh():
    """JWT 토큰 리프레시"""
    user_oid = get_jwt_identity()
    return response_200({
        'access_token': create_access_token(
            identity=user_oid,
            expires_delta= timedelta(Config.JWT_ACCESS_TOKEN_EXPIRES)
        ),
        'refresh_token': create_refresh_token(
            identity=user_oid,
            expires_delta= timedelta(Config.JWT_ACCESS_TOKEN_EXPIRES)
        ),
    })


@api.get("/auth-test")
@jwt_required()
@timer
def auth_test_api():
    """인증 테스트"""
    return response_200("hello, %s" % get_jwt_identity())


@api.delete("/withdrawal")
@timer
@login_required
@Validator(bad_request)
def auth_withdrawal_api(
    pw=Json(str, rules=MinLen(8))
):
    """회원 탈퇴"""
    user = User(current_app.db).get_password(g.user_oid)
    # 비밀번호 확인 검증
    if not check_password_hash(user['password'], pw):
        return forbidden("Authentication failed.")
    return no_content
