from app.api.decorator import login_required, timer
from app.api.response import (bad_request, created, forbidden, no_content,
                              not_found, response_200)
from app.api.validation import ObjectIdValid
from bson import ObjectId
from flask import current_app, g
from flask_validation_extended import Route, Validator
from model.mongodb import User

from . import api_v1 as api


@api.get("/bookmarks")
@timer
@login_required
@Validator(bad_request)
def api_v1_get_bookmarks():
    """ 북마크 리스트 반환 API"""
    model = User(current_app.db)

    return response_200(
        model.get_bookmarks(ObjectId(g.user_oid))
    )

@api.put('/bookmarks/<detection_id>')
@timer
@login_required
@Validator(bad_request)
def api_v1_insert_bookmark(
    detection_id: str = Route(str, rules=ObjectIdValid()),
):
    """ 북마크 추가 API"""
    model = User(current_app.db)

    is_exist = model.is_exist_detection_id(
        ObjectId(g.user_oid), 
        ObjectId(detection_id)
    )
    if not is_exist:
        # 중복 추가할 경우 -> Forbidden
        return forbidden("no access")

    model.upsert_bookmarks(
        ObjectId(g.user_oid),
        ObjectId(detection_id))

    return created

@api.delete('/bookmarks/<detection_id>')
@timer
@login_required
@Validator(bad_request)
def api_v1_delete_bookmark(
    detection_id=Route(str, rules=ObjectIdValid())
):
    """북마크 삭제 API"""
    model = User(current_app.db)

    bookmarks = model.get_bookmarks(ObjectId(g.user_oid))
    if detection_id not in bookmarks:
        return not_found
    else:
        model.delete_bookmarks(
            ObjectId(g.user_oid),
            ObjectId(detection_id)
        )
        return no_content