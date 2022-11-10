"""User 관련 APIs"""
from flask import g, current_app
from flask_validation_extended import Json, Route, File
from flask_validation_extended import Validator, MinLen, Ext
from bson.objectid import ObjectId
from app.api.response import response_200, created
from app.api.response import bad_request
from app.api.decorator import login_required, timer
from app.api.validation import ObjectIdValid
from controller.util import remove_none_value
from controller.file_util import upload_to_s3
from model.mongodb import User
from . import api_v1 as api


@api.get("/users/me")
@timer
@login_required
def api_v1_get_users_me():
    """내 정보 반환 API"""
    return response_200(
        User(current_app.db).get_userinfo(g.user_oid)
    )


@api.put("/users/me")
@timer
@login_required
@Validator(bad_request)
def api_v1_update_users_me(
    name=Json(str, rules=MinLen(1), optional=True),
    introduction=Json(str, rules=MinLen(1), optional=True)
):
    """내 정보 갱신 API"""
    new_info = remove_none_value(locals())
    User(current_app.db).update_user(g.user_oid, new_info)

    # TODO: 캐싱된 모든 곳 갱신해야 함
    return created


@api.put("/users/me/photo")
@timer
@login_required
@Validator(bad_request)
def api_v1_update_users_me_photo(
    photo=File(rules=Ext(['.png', '.jpg', '.jpeg', '.gif']))
):
    """내 사진 갱신 API"""
    path = upload_to_s3(
        s3=current_app.s3,
        file=photo,
        type='profile',
        object_id=str(g.user_oid)
    )[0]

    # TODO: 캐싱된 모든 곳 갱신해야 함
    return created


@api.get("/users/<user_oid>")
@timer
@login_required
def api_v1_get_user(
    user_oid=Route(str, rules=ObjectIdValid())
):
    """특정 사용자 정보 반환 API"""
    return response_200(
        User(current_app.db).get_userinfo(ObjectId(user_oid))
    )
