from bson import ObjectId
from flask import g, current_app
from flask_validation_extended import Route
from flask_validation_extended import Validator
from app.api.response import response_200, created, forbidden, no_content, not_found
from app.api.response import bad_request
from app.api.decorator import login_required, timer
from app.api.validation import ObjectIdValid
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

    bookmarks = model.get_bookmarks(ObjectId(g.user_oid))
    if detection_id in bookmarks:
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