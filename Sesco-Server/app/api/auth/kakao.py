from flask_validation_extended import Validator
from app.api.response import bad_request
from app.api.decorator import timer
from . import api_auth as api


@api.route("/oauth/kakao", methods=["GET", "POST"])
@Validator(bad_request)
@timer
def kakao_oauth_api():
    """카카오 Oauth 검증"""
    ...
