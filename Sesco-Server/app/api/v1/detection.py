from bson import ObjectId
from flask import g, current_app
from flask_validation_extended import Json, Route, Query
from flask_validation_extended import Validator, MinLen
from app.api.response import response_200, created, forbidden, no_content
from app.api.response import bad_request
from app.api.decorator import login_required, timer
from app.api.validation import ObjectIdValid
from model.mongodb import User, Detection, MasterConfig
from . import api_v1 as api

@api.get("/detection")
@timer
@login_required
@Validator(bad_request)
def api_v1_get_detection(
    skip: int = Query(int, default=0, optional=True),
    limit: int = Query(int, default=0, optional=True)
):
    """ 탐지 기록 리스트 반환 API"""
    model = Detection(current_app.db)

    return response_200(
        model.get_detections(skip=skip, limit=limit)
    )



@api.get("/detection/<detection_id>")
@timer
@login_required
@Validator(bad_request)
def api_v1_get_detection_one(
    detection_id: str = Route(str, rules=ObjectIdValid())
):
    """탐지 기록 단일 조회 API"""
    model = Detection(current_app.db)
    return response_200(
        model.get_detection_one(ObjectId(detection_id))
    )


@api.post('/detection')
@timer
@login_required
@Validator(bad_request)
def api_v1_insert_detection(
    img=Json(str, rules=MinLen(1)),
    name=Json(str, rules=MinLen(1)),
    category=Json(str, rules=MinLen(1)),
    location=Json(str, rules=MinLen(1)),
    coordinate=Json(dict)
):
    """ 병해충 탐지 추가 API"""
    user_model = User(current_app.db)
    detection_model = Detection(current_app.db)
    
    # TODO: AI 모델로부터 결과 받아오기
    result = None # AI(img, category)
    
    # TODO: message
    message = None


    
    user = user_model.get_userinfo(g.user_oid)

    # name, category, location, result 담기
    search_str = None

    detection_model.insert_detection({
        'user_name': user['name'],
        'user_img': user['img'],
        'user_id': user['_id'],
        'name': name,
        'img': img,
        'category': category,
        'location': location,
        'coordinate': coordinate,
        'result': result,
        'message': message,
        'search_str':search_str,
    }).inserted_id

    return created



@api.delete('/detection/<detection_id>')
@timer
@login_required
@Validator(bad_request)
def api_v1_delete_detection(
    detection_id=Route(str, rules=ObjectIdValid())
):
    """탐지기록 삭제 API"""
    detection_model = Detection(current_app.db)
    
    detection = detection_model.get_detection_one(ObjectId(detection_id))
    if detection['user_id'] != g.user_oid:
        return forbidden("No permission")
    
    detection_model.delete_detection(ObjectId(detection_id))

    return no_content



@api.get("/detection/solution")
@timer
@login_required
@Validator(bad_request)
def api_v1_get_solution(
    disease=Json(str, rules=MinLen(1))
):
    """대처 방안 반환 API"""
    model = MasterConfig(current_app.db)

    return response_200(
        model.get_solution(disease)
    )


@api.get("/search")
@timer
@login_required
@Validator(bad_request)
def api_v1_search(
    search_str=Json(str, rules=MinLen(1))
):
    """통합 검색 API"""
    model = Detection(current_app.db)

    return response_200(
        model.get_search(search_str)
    )
