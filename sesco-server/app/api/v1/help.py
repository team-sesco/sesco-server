from bson import ObjectId
from uuid import uuid4
from flask import g, current_app
from flask_validation_extended import Json, Route, Query, File
from flask_validation_extended import Validator, MinLen, Ext, MaxFileCount
from app.api.response import response_200, created, forbidden, no_content
from app.api.response import bad_request
from app.api.decorator import login_required, admin_required, timer
from app.api.validation import ObjectIdValid
from controller.file_util import upload_to_s3
from controller.util import remove_none_value
from model.mongodb import User
from model.mongodb import Help
from . import api_v1 as api


@api.post('/help')
@timer
@login_required
@Validator(bad_request)
def api_v1_insert_help(
    imgs=Json(list, optional=True),
    content=Json(str, rules=MinLen(1))
):
    """문의 추가 API"""
    user_model = User(current_app.db)
    help_model = Help(current_app.db)

    user = user_model.get_userinfo(g.user_oid)

    help_model.insert_help({
        'user_id': user['_id'],
        'user_name': user['name'],
        'user_img': user['img'],
        'imgs': imgs,
        'content': content
    })
    return created


@api.post("/help/photos")
@timer
@login_required
@Validator(bad_request)
def api_v1_post_help_photo(
    imgs: File = File(
        rules=[
            Ext(['.png', '.jpg', '.jpeg', '.gif']),
            MaxFileCount(10)
        ]
    )
):
    """문의 이미지 업로드 API"""
    return response_200(
        upload_to_s3(
            s3=current_app.s3,
            files=imgs,
            type="help",
            object_id=f"{g.user_oid}_{uuid4()}"
        )
    )


@api.get("/help")
@timer
@admin_required
@Validator(bad_request)
def api_v1_get_helps(
    status: str = Query(str, default=None, optional=True),
    skip: int = Query(int, default=0, optional=True),
    limit: int = Query(int, default=0, optional=True)
):
    """문의 목록 조회 API"""
    model = Help(current_app.db)
    return response_200(
        model.get_helps(
            status=status,
            skip=skip,
            limit=limit
        )
    )


@api.get("/help/<help_oid>")
@timer
@admin_required
@Validator(bad_request)
def api_v1_get_help(
    help_oid: str = Route(str, rules=ObjectIdValid())
):
    """문의 단일 조회 API"""
    model = Help(current_app.db)
    return response_200(
        model.get_help_one(ObjectId(help_oid))
    )


@api.put("/help/<help_oid>")
@timer
@admin_required
@Validator(bad_request)
def api_v1_update_help_status(
    help_oid: str = Route(str, rules=ObjectIdValid()),
    status: str = Query(str, rules=MinLen(1))
):
    """문의 처리 API"""
    if status not in set(["pending", "complete"]):
        return "wrong parameter (status)"
    new_info = remove_none_value(locals())
    Help(current_app.db).update_help(ObjectId(help_oid), new_info)
    return created