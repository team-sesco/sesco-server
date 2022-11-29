"""
Admin Auth APIs
"""
from flask_validation_extended import Validator, Json, MinLen
from flask_jwt_extended import create_refresh_token, create_access_token
from app.api.response import response_200, bad_request, unauthorized
from app.api.decorator import timer, admin_required
from datetime import timedelta
from config import Config
from . import api_admin as api


@api.post('/auth/sign-in')
@Validator(bad_request)
@timer
def admin_auth_signin_api(
    id=Json(str, rules=MinLen(5)),
    pw=Json(str, rules=MinLen(5))
):
    """로그인"""
    if (
        id != Config.ADMIN_ID
        or pw != Config.ADMIN_PW
    ):
        return unauthorized("Authentication failed.")
    return response_200({
        'access_token': create_access_token(id, expires_delta= timedelta(Config.JWT_ACCESS_TOKEN_EXPIRES)),
        'refresh_token': create_refresh_token(id, expires_delta= timedelta(Config.JWT_ACCESS_TOKEN_EXPIRES))
    })


@api.route("/auth/auth-test")
@admin_required
@timer
def admin_auth_test_api():
    """인증 테스트"""
    return response_200("hello, Sesco-ADMIN!")