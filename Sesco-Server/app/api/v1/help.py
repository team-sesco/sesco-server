from bson import ObjectId
from flask import g, current_app
from flask_validation_extended import Json, Route, Query
from flask_validation_extended import Validator, Min, MinLen, In
from app.api.response import response_200, created, forbidden, no_content
from app.api.response import bad_request
from app.api.decorator import login_required, timer
from app.api.validation import ObjectIdValid
from controller.util import remove_none_value
from model.mongodb import User
from model.mongodb import Help
from . import api_v1 as api

@api.post('/help')
@timer
@login_required
@Validator(bad_request)
def api_v1_insert_help(
    # 이미지 리스트로 받아도 될까?
    imgs=Json(list, optional=True),
    content=Json(str, rules=MinLen(1))
):
    """문의 추가 API"""
    user_model = User(current_app.db)
    help_model = Help(current_app.db)

    user = user_model.get_userinfo(g.user_oid)

    help_model.insert_help({
        'user_id':user['_id'],
        'user_name':user['name'],
        'user_img':user['img'],
        'imgs':imgs,
        'content':content
    })
    return created

@api.get("/help")
@timer
@login_required
@Validator(bad_request)
def api_v1_get_helps(
    skip: int = Query(int, default=0, optional=True),
    limit: int = Query(int, default=0, optional=True)
):
    """문의 목록 조회 API"""
    model = Help(current_app.db)
    return response_200(
        model.get_helps(skip=skip, limit=limit)
    )


@api.get("/help/<help_id>")
@timer
@login_required
@Validator(bad_request)
def api_v1_get_help(
    help_id: str = Route(str, rules=ObjectIdValid())
):
    """문의 단일 조회 API"""
    model = Help(current_app.db)
    return response_200(
        model.get_help_one(ObjectId(help_id))
    )

@api.delete('/help/<help_id>')
@timer
@login_required
@Validator(bad_request)
def api_v1_delete_help(
    help_id=Route(str, rules=ObjectIdValid())
):
    """문의 삭제 API"""
    model = Help(current_app.db)

    help = model.get_help_one(ObjectId(help_id))
    if help['user_id'] != g.user_oid:
        return forbidden("No permission")

    model.delete_help(ObjectId(help_id))

    return no_content