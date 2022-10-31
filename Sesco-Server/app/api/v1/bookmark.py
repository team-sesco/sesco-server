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
        model.get_bookmarks(
            ObjectId(g.user_oid),
            skip=skip,
            limit=limit)
    )
"""
COMMENT
북마크 추가 단 API는 전체적으로 수정이 필요해보임 !
쿼리로 간단하게 추가 가능한데, 너는 지금 기존 쿼리를 가져와서 리스트에 넣고 중복제거하고 다시 업데이트를 시키는 중 (앱단 처리 방식)

최대한 쿼리로 해결하는 방식으로 다시 생각해보시길!
"""
@api.put('/bookmarks/<detection_id>')
@timer
@login_required
@Validator(bad_request)
def api_v1_insert_bookmark(
    detection_id: str = Route(str, rules=ObjectIdValid()),
):
    """ 북마크 추가 API"""
    model = User(current_app.db)

    
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

    result = model.get_bookmarks(
        ObjectId(g.user_oid)).get('bookmarks', [])

    if ObjectId(detection_id) in result:
        result.remove(ObjectId(detection_id))
        model.update_bookmarks(
            ObjectId(g.user_oid),
            list(set(result))
        )
        return no_content
    else:
        return not_found