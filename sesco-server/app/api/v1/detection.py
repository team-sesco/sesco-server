import requests
from bson import ObjectId
from uuid import uuid4
from flask import g, current_app
from flask_validation_extended import Json, Route, Query, File
from flask_validation_extended import Validator, MinLen, Ext, MaxFileCount
from app.api.response import response_200, created, forbidden, no_content, not_found
from app.api.response import bad_request
from app.api.decorator import login_required, timer
from app.api.validation import ObjectIdValid
from controller.file_util import upload_to_s3
from model.mongodb import User, Detection, MasterConfig
from config import config
from datetime import datetime
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
    results = model.get_detections(
                user_oid=g.user_oid,
                skip=skip,
                limit=limit
            )

    for result in results:
        result['created_at'] = result['created_at'].strftime("%Y년 %m월 %d일 %H시 %M분")
        del result['search_str']

    return response_200(
        results
    )


@api.get("/detection/<detection_oid>")
@timer
@login_required
@Validator(bad_request)
def api_v1_get_detection_one(
    detection_oid: str = Route(str, rules=ObjectIdValid())
):
    """탐지 기록 단일 조회 API"""
    model = Detection(current_app.db)
    result = model.get_detection_one(ObjectId(detection_oid))
    result['created_at'] = result['created_at'].strftime("%Y년 %m월 %d일 %H시 %M분")
    del result['search_str']

    return response_200(
        result
    )


@api.post("/detection/photo")
@timer
@login_required
@Validator(bad_request)
def api_v1_post_detection_photo(
    img: File = File(
        rules=[
            Ext(['.png', '.jpg', '.jpeg', '.gif', '.heic']),
            MaxFileCount(1)
        ]
    )
):
    """ 탐지 사진 업로드 API"""
    return response_200(
        upload_to_s3(
            s3=current_app.s3,
            files=img,
            type="detection",
            object_id=f"{g.user_oid}_{uuid4()}"
        )[0]
    )


@api.post('/detection')
@timer
@login_required
@Validator(bad_request)
def api_v1_insert_detection(
    img=Json(str, rules=MinLen(1)),
    category=Json(str, rules=MinLen(1)),
    location=Json(dict)
):
    """ 병해충 탐지 추가 API"""
    user_model = User(current_app.db)
    detection_model = Detection(current_app.db)

    user = user_model.get_userinfo(g.user_oid)

    # model_result에는 '작물 정상' 또는 '작물 병해충 이름'으로 들어온다.
    model_result = requests.get(
        headers={"SESCO-API-KEY": config.AI_SERVER_API_KEY},
        url=f"{config.AI_SERVER_DOMAIN}/api/v1/predict"
        f"?category={category}"
        f"&img={img}"
    )
    if model_result.status_code != 200:
        return bad_request(model_result.json()['description'])
    model_result = model_result.json()

    message = [
        {'sender': 'bot', 'content': '안녕하세요! 세스코입니다.'},
    ]
    if model_result['result'][-2:] == "정상":
        message.append(
            {'sender': 'bot', 'content': '감지된 병해충이 없습니다.'}
        )
    else:
        message.append(
            {
                'sender': 'bot',
                'content': f"{user['name']}님의 작물에서, 병해충 \"{model_result['result']}\"이 감지되었습니다."
            }
        )

    detection_info = {
        'user_name': user['name'],
        'user_img': user['img'],
        'user_id': user['_id'],
        'name': model_result['result']['name'],
        'img': img,
        'category': category,
        'location': location,
        'data': {
            'name': model_result['result'],
            'ratio': None,
            'visualize': None
        },
        'message': message,
        'search_str': f"{model_result['result']} {category} {location['address_name']}",
    }
    
    detection_model.insert_detection(detection_info)
    del detection_info['search_str']
    detection_info['created_at'] = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")

    return response_200(
        detection_info
    )


@api.get('/detection/visualize/<detection_id>')
@timer
@login_required
@Validator(bad_request)
def api_v1_get_visualize(
    detection_id=Route(str, rules=ObjectIdValid())
):
    """탐지 시각화 자료 반환 API"""
    detection_model = Detection(current_app.db)

    detection = detection_model.get_detection_one(ObjectId(detection_id))
    if detection is None:
        return not_found
    
    if detection['user_id'] != g.user_oid:
        return forbidden("No permission")
    
    # 이미 ratio, visualize가 존재하는 경우 -> 탐지기록 바로 반환
    if detection['data']['ratio'] != None and detection['data']['visualize'] != None:
        del detection['search_str']
        return detection

    # ratio, visualize 중 하나라도 None일 경우 -> AI server에 요청
    model_result = requests.get(
        headers={"SESCO-API-KEY": config.AI_SERVER_API_KEY},
        url=f"{config.AI_SERVER_DOMAIN}/api/v1/visualize"
        f"?category={detection['data']['category']}"
        f"&img={detection['data']['img']}"
        f"&disease={detection['data']['name']}"
    )

    result = {
        '_id': ObjectId(detection_id),
        'ratio': model_result['result']['ratio'],
        'visualize': model_result['result']['visualize']
    }

    detection_model.update_one(result)

    return result


@api.get("/detection/solution")
@timer
@login_required
@Validator(bad_request)
def api_v1_get_solution(
    disease=Query(str, rules=MinLen(1))
):
    """대처 방안 반환 API"""
    model = MasterConfig(current_app.db)
    result = model.get_value('pest_dict')
    return response_200(result['value'][disease])


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
