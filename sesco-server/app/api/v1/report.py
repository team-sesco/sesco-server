from bson import ObjectId
from flask import g, current_app
from flask_validation_extended import Json, Route, Query
from flask_validation_extended import Validator, MinLen
from app.api.response import response_200, created, forbidden, no_content
from app.api.response import bad_request
from app.api.decorator import login_required, admin_required, timer
from app.api.validation import ObjectIdValid
from model.mongodb import Report
from . import api_v1 as api


@api.post('/report')
@timer
@login_required
@Validator(bad_request)
def api_v1_insert_report(
    type=Json(str, rules=MinLen(1)),
    target_id=Json(str, rules=MinLen(1)),
    content=Json(str, rules=MinLen(1), optional=True)
):
    """신고 추가 API"""
    model = Report(current_app.db)
    model.insert_report({
        'target_id': ObjectId(target_id),
        'user_id': ObjectId(g.user_oid),
        'type': type,
        'content': content
    })

    return created


@api.get("/report")
@timer
@admin_required
@Validator(bad_request)
def api_v1_get_reports(
    status: str = Query(str, default=None, optional=True),
    skip: int = Query(int, default=0, optional=True),
    limit: int = Query(int, default=0, optional=True)
):
    """신고 목록 조회 API"""
    model = Report(current_app.db)
    return response_200(
        model.get_reports(
            status=status,
            skip=skip,
            limit=limit
        )
    )


@api.get("/report/<report_id>")
@timer
@admin_required
@Validator(bad_request)
def api_v1_get_report(
    report_id: str = Route(str, rules=ObjectIdValid())
):
    """신고 단일 조회 API"""
    model = Report(current_app.db)
    return response_200(
        model.get_report_one(ObjectId(report_id))
    )
