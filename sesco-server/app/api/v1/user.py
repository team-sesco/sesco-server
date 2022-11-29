"""User 관련 APIs"""
from flask import g, current_app
from flask_validation_extended import Json, Route, File
from flask_validation_extended import Validator, MinLen, Ext, MaxFileCount, MaxLen
from bson.objectid import ObjectId
from app.api.response import response_200, created, no_content, conflict
from app.api.response import bad_request
from app.api.decorator import login_required, timer
from app.api.validation import ObjectIdValid
from controller.util import remove_none_value
from controller.file_util import upload_to_s3
from model.mongodb import User, Detection, Post, Help
from . import api_v1 as api


@api.get("/users/me")
@timer
@login_required
def api_v1_get_users_me():
    """내 정보 반환 API"""
    result = User(current_app.db).get_userinfo(g.user_oid)
    del result['password']
    return response_200(
        result
    )


@api.put("/users/me")
@timer
@login_required
@Validator(bad_request)
def api_v1_update_users_me(
    name=Json(str, rules=[MinLen(3), MaxLen(20)], optional=True),
    img=Json(str, rules=MinLen(1), optional=True)
):
    """내 정보 갱신 API"""
    new_info = remove_none_value(locals())

    # 닉네임 중복 확인
    if name is not None:
        if User(current_app.db).get_user_by_name(name) is not None:
            return conflict("닉네임이 중복되었습니다.")

    # 유저 정보 갱신
    User(current_app.db).update_user(g.user_oid, new_info)
    # TODO: 모든 유저의 북마크에 대해, 유저의 닉네임을 변경해야한다.



    # 캐싱 정보 갱신
    new_info = remove_none_value({
        "user_name": new_info.get('name', None),
        'user_img': new_info.get('img', None) 
    })
    for col in [Post, Detection, Help]:
        col(current_app.db).update_user(
            g.user_oid,
            new_info
        )

    return created


@api.post("/users/me/photo")
@timer
@login_required
@Validator(bad_request)
def api_v1_update_users_me_photo(
    photo: File = File(
        rules=[
            Ext(['.png', '.jpg', '.jpeg', '.gif', '.heic']),
            MaxFileCount(1)
        ]
    )
):
    """ 사용자 사진 업로드 API"""
    # TODO: Scheduler or 30 days limit
    return response_200(
        upload_to_s3(
            s3=current_app.s3,
            files=photo,
            type='profile',
            object_id=str(g.user_oid)
        )[0]
    )


@api.get("/users/<user_oid>")
@timer
@login_required
def api_v1_get_user(
    user_oid=Route(str, rules=ObjectIdValid())
):
    result = User(current_app.db).get_userinfo(ObjectId(user_oid))
    del result['password']
    """특정 사용자 정보 반환 API"""
    return response_200(
        result
    )

@api.delete("/users/me")
@timer
@login_required
def api_v1_delete_user():
    User(current_app.db).delete_user(g.user_oid)
    Detection(current_app.db).delete_detection_all(g.user_oid)
    """회원 탈퇴 API"""
    return no_content