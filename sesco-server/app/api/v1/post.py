from bson import ObjectId
from flask import g, current_app
from flask_validation_extended import Json, Route, Query
from flask_validation_extended import Validator, MinLen
from app.api.response import response_200, created, forbidden, no_content
from app.api.response import bad_request
from app.api.decorator import login_required, timer
from app.api.validation import ObjectIdValid
from controller.util import remove_none_value
from model.mongodb import User
from model.mongodb import Post
from . import api_v1 as api


@api.get("/post")
@timer
@login_required
@Validator(bad_request)
def api_v1_get_posts(
    skip: int = Query(int, default=0, optional=True),
    limit: int = Query(int, default=0, optional=True)
):
    """게시글 목록 조회 API"""
    model = Post(current_app.db)
    return response_200(
        model.get_posts(skip=skip, limit=limit)
    )


@api.get("/post/<post_id>")
@timer
@login_required
@Validator(bad_request)
def api_v1_get_post(
    post_id: str = Route(str, rules=ObjectIdValid())
):
    """게시글 단일 조회 API"""
    model = Post(current_app.db)
    return response_200(
        model.get_post_one(ObjectId(post_id))
    )


@api.post('/post')
@timer
@login_required
@Validator(bad_request)
def api_v1_insert_post(
    name=Json(str, rules=MinLen(1)),
    content=Json(str, rules=MinLen(1)),
    type=Json(str, rules=MinLen(1))
):
    """게시글 추가 API"""
    user_model = User(current_app.db)
    post_model = Post(current_app.db)

    user = user_model.get_userinfo(g.user_oid)
    post_model.insert_post({
        'name': name,
        'content': content,
        'user_id': user['_id'],
        'user_name': user['name'],
        'user_img': user['img'],
        'type': type
    })

    return created


@api.put('/post/<post_oid>')
@timer
@login_required
@Validator(bad_request)
def api_v1_update_post(
    post_oid=Route(str, rules=ObjectIdValid()),
    name=Json(str, rules=MinLen(1), optional=True),
    content=Json(str, rules=MinLen(1), optional=True),
    img=Json(str, rules=MinLen(1), optional=True)
):
    """게시글 수정 API"""
    new_info = remove_none_value(locals())
    del new_info['post_oid']

    post_model = Post(current_app.db)

    post = post_model.get_post_one(ObjectId(post_oid))
    if post['user_id'] != g.user_oid:
        return forbidden("No permission")

    post_model.update_post(ObjectId(post_oid), new_info)
    return created


@api.delete('/post/<post_oid>')
@timer
@login_required
@Validator(bad_request)
def api_v1_delete_post(
    post_oid=Route(str, rules=ObjectIdValid())
):
    """게시글 삭제 API"""
    post_model = Post(current_app.db)

    post = post_model.get_post_one(ObjectId(post_oid))
    if not post:
        return bad_request("No post")
    if post['user_id'] != g.user_oid:
        return forbidden("No permission")
    post_model.delete_post(ObjectId(post_oid))

    return no_content
