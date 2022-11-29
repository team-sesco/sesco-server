from app.api.decorator import login_required, timer
from app.api.response import (bad_request, created, forbidden, no_content,
                              not_found, response_200)
from app.api.validation import ObjectIdValid
from bson import ObjectId
from flask import current_app, g
from flask_validation_extended import Route, Validator, Query
from model.mongodb import User, Detection

from . import api_v1 as api


@api.get("/bookmarks")
@timer
@login_required
@Validator(bad_request)
def api_v1_get_bookmarks(
    limit: int = Query(int, default=None, optional=True)
):
    """ 북마크 리스트 반환 API"""
    model = User(current_app.db)

    return response_200(
        list(reversed(model.get_bookmarks(
            g.user_oid, limit
        )['bookmarks']
    )))


@api.put('/bookmarks/<detection_oid>')
@timer
@login_required
@Validator(bad_request)
def api_v1_insert_bookmark(
    detection_oid: str = Route(str, rules=ObjectIdValid()),
):
    """ 북마크 추가 API"""
    model = User(current_app.db)

    if model.get_user_by_bookmark(
        g.user_oid,
        ObjectId(detection_oid)
    ):
        return forbidden("Already bookmarked")

    detection = Detection(current_app.db).get_detection_one(
        ObjectId(detection_oid)
    )
    if not detection:
        return not_found

    model.upsert_bookmarks(
        g.user_oid,
        {
            "is_me": detection['user_id'] == g.user_oid,
            "detection_id": detection['_id'],
            "detection_category": detection['category'],
            "detection_location": detection['location'],
            "detection_result": detection['model_result']
        }
    )
    return created


@api.delete('/bookmarks/<detection_oid>')
@timer
@login_required
@Validator(bad_request)
def api_v1_delete_bookmark(
    detection_oid=Route(str, rules=ObjectIdValid())
):
    """북마크 삭제 API"""
    User(current_app.db).delete_bookmarks(
        g.user_oid,
        ObjectId(detection_oid)
    )
    return no_content