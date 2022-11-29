from bson import ObjectId
from flask import g, current_app
from flask_validation_extended import Json, Route, Query
from flask_validation_extended import Validator, MinLen
from app.api.response import response_200, created, forbidden, no_content
from app.api.response import bad_request
from app.api.decorator import login_required, timer, admin_required
from app.api.validation import ObjectIdValid
from model.mongodb import Notification
from . import api_v1 as api

@api.post('/notification')
@timer
@login_required
@Validator(bad_request)
def api_v1_insert_notification(
    user_device_token=Json(str, rules=MinLen(1)),
    content=Json(str, rules=MinLen(1)),
    type=Json(str, rules=MinLen(1))
):
    """ 알림 추가 API"""
    model = Notification(current_app.db)

    model.insert_notification({
        'user_id': ObjectId(g.user_oid),
        'user_device_token': user_device_token,
        'type': type,
        'content': content
    })

    return created

@api.get("/notification")
@timer
@login_required
@Validator(bad_request)
def api_v1_get_notification(
    skip: int = Query(int, default=0, optional=True),
    limit: int = Query(int, default=0, optional=True)
):
    """ 알림 리스트 반환 API"""
    model = Notification(current_app.db)
    user_notification = model.get_user_notifications(
        user_oid=g.user_oid,
        skip=skip,
        limit=limit
    )
    notice_notification = model.get_notifications(skip=skip, limit=limit)

    return response_200(
        notice_notification+user_notification
    )



@api.get("/notification/<notification_oid>")
@timer
@login_required
@Validator(bad_request)
def api_v1_get_notification_one(
    notification_oid: str = Route(str, rules=ObjectIdValid())
):
    """ 알림 단일 조회 API"""
    model = Notification(current_app.db)
    return response_200(
        model.get_notification_one(ObjectId(notification_oid))
    )



@api.delete('/notification/<notification_oid>')
@timer
@admin_required
@Validator(bad_request)
def api_v1_delete_notification(
    notification_oid=Route(str, rules=ObjectIdValid())
):
    """ 알림 삭제 API"""
    model = Notification(current_app.db)
    
    detection = model.get_notification_one(ObjectId(notification_oid))
    if detection['user_id'] != g.user_oid:
        return forbidden("No permission")
    
    model.delete_notification(ObjectId(notification_oid))

    return no_content

