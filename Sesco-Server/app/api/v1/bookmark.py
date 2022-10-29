from bson import ObjectId
from flask import g, current_app
from flask_validation_extended import Json, Route, Query
from flask_validation_extended import Validator, Min, MinLen
from app.api.response import response_200, created, forbidden, no_content, not_found
from app.api.response import bad_request
from app.api.decorator import login_required, timer
from app.api.validation import ObjectIdValid
from controller.util import remove_none_value
from model.mongodb import User, Detection, MasterConfig
from markupsafe import escape
from . import api_v1 as api

@api.get("/bookmarks")
@timer
@login_required
@Validator(bad_request)
def api_v1_get_bookmarks(
    skip: int = Query(int, default=0, optional=True),
    limit: int = Query(int, default=0, optional=True)
):
    """ 북마크 리스트 반환 API"""
    model = User(current_app.db)
    return response_200(
        model.get_bookmarks(ObjectId(g.user_oid), skip=skip, limit=limit)
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

    result = list(model.get_bookmarks(
        ObjectId(g.user_oid)).get('bookmarks', []))
    result.append(ObjectId(detection_id))
    model.update_bookmarks(
        ObjectId(g.user_oid),
        list(set(result)) # 중복 제거
    )

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

    result = list(model.get_bookmarks(
        ObjectId(g.user_oid)).get('bookmarks', []))

    if ObjectId(detection_id) in result:
        result.remove(ObjectId(detection_id))
        model.update_bookmarks(
            ObjectId(g.user_oid),
            list(set(result))
        )
        return no_content
    else:
        return not_found