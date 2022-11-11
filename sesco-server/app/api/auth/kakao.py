from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_validation_extended import Validator, Json
from app.api.response import bad_request, response_200
from app.api.decorator import timer
from controller.auth.kakao import get_userinfo
from model.mongodb import User
from . import api_auth as api


@api.post("/oauth/kakao")
@Validator(bad_request)
@timer
def kakao_oauth_api(
    access_token=Json(str)
):
    """카카오 Oauth 검증"""

    # Get Kakao User Info
    kakao_user = get_userinfo(access_token)

    # Get SESCO User Info
    model = User(current_app.db)
    user = model.get_password_with_id(
        f"kakao_{kakao_user['id']}"
    )

    if user:
        user_oid = str(user['_id'])
    else:
        # TODO: Device Token을 위해 나중에 FCM 작업시에 필드 추가해야함.
        document = {
            'id': f"kakao_{kakao_user['id']}",
            'name': f"kakao_{kakao_user['id']}",
            'auth_type': 'kakao'
        }
        user_oid = model.insert_user(document).inserted_id

    return response_200({
        'access_token': create_access_token(identity=user_oid),
        'refresh_token': create_refresh_token(identity=user_oid),
    })
