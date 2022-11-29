import requests
from bson import ObjectId
from uuid import uuid4
from flask import g, current_app
from flask_validation_extended import Json, Route, Query, File
from flask_validation_extended import Validator, MinLen, Ext, MaxFileCount, Min
from app.api.response import response_200, created, forbidden, no_content, not_found
from app.api.response import bad_request
from app.api.decorator import login_required, timer
from app.api.validation import ObjectIdValid
from controller.file_util import upload_to_s3
from model.mongodb import User, Detection, Notification
from config import config
from datetime import datetime, timedelta
from . import api_v1 as api
from time import time

@api.get('/detection')
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
    user_model = User(current_app.db)
    result = model.get_detection_one(ObjectId(detection_oid))
    exist = user_model.get_user_by_bookmark(g.user_oid, ObjectId(detection_oid))
    if result is None:
        return forbidden("No Permission")
    result['created_at'] = result['created_at'].strftime("%Y년 %m월 %d일 %H시 %M분")
    del result['search_str']
    result['is_bookmarked'] = False if exist is None else True
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


@api.post('/detection/predict')
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

    model_result = requests.get(
        headers={"SESCO-API-KEY": config.AI_SERVER_API_KEY},
        url=f"{config.AI_SERVER_DOMAIN}/api/v1/predict"
        f"?category={category}"
        f"&img={img}"
    )
    if model_result.status_code != 200:
        return bad_request(model_result.json()['description'])
    model_result = model_result.json()

    detection_info = {
        'user_name': user['name'],
        'user_img': user['img'],
        'user_id': user['_id'],
        'img': img,
        'category': category,
        'location': location,
        'model_result': {
            'name': model_result['result']['name'],
            'ratio': model_result['result']['ratio'],
            'img': None,
            'unidentified': True if model_result['result']['check'] == "미확인" else False
        },
        'is_detected': False if model_result['result']['name'][-2:] == "정상" else True,
        'search_str': f"{model_result['result']['name']} {category} {location['address_name']}",
    }
    
    detection_oid = detection_model.insert_detection(detection_info).inserted_id

    if detection_info['is_detected']:
        notification_model = Notification(current_app.db)
        notification_model.insert_notification({
            'user_id': g.user_oid,
            'user_device_token': user['device_token'],
            'content': f"{location['address_name']}에서 {model_result['result']['name']}이 탐지되었습니다.",
            'type': "Detection"
        })


    return response_200(
        {
            'model_result': {
                'name': detection_info['model_result']['name'],
                'unidentified': detection_info['model_result']['unidentified']
            },
            'user_name': detection_info['user_name'],
            'created_at': datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분"),
            'location': detection_info['location']['address_name'],
            'detection_oid': detection_oid,
            'is_detected': detection_info['is_detected']
        }
    )

@api.post('/detection/visualize/<detection_oid>')
@timer
@login_required
@Validator(bad_request)
def api_v1_visualize(
    img=Json(str, rules=MinLen(1)),
    category=Json(str, rules=MinLen(1)),
    disease=Json(str, rules=MinLen(1)),
    detection_oid: str = Route(str, rules=ObjectIdValid())
):
    detection_model = Detection(current_app.db)
    detection = detection_model.get_detection_one(ObjectId(detection_oid))

    if detection is None:
        return forbidden("No Permission")

    if detection['model_result']['img'] is None:
        model_result = requests.get(
            headers={"SESCO-API-KEY": config.AI_SERVER_API_KEY},
            url=f"{config.AI_SERVER_DOMAIN}/api/v1/visualization"
            f"?category={category}"
            f"&img={img}"
            f"&disease={disease}"
        )

        if model_result.status_code != 200:
            return bad_request(model_result.json()['description'])
        model_result = model_result.json()
        visualization_img = model_result['result']
        update_detection = {
            '_id': ObjectId(detection_oid),
            'model_result.img': visualization_img
        }
        detection_model.upsert_one(
            update_detection
        )
    
    return response_200(
        {
            'ratio': detection['model_result']['ratio'],
            'visualization': visualization_img,
            'location': detection['location'],
        }
    )

@api.get("/detection/solution")
@timer
@login_required
@Validator(bad_request)
def api_v1_get_solution(
    disease=Query(str, rules=MinLen(1))
):
    disease = disease.replace('_', ' ')
    """대처 방안 반환 API"""
    return response_200(g.get('pest_dict')[disease])

@api.post("/detection/map")
@timer
@login_required
@Validator(bad_request)
def api_v1_get_detection_by_location(
    location=Json(dict),
):
    print(f'들어온 location = {location}')
    model = Detection(current_app.db)
    result = model.get_detection_by_location(location)
    print(f'가져온 데이터 = {result}')
    return response_200(result)
    


@api.post("/search")
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

@api.get("/detection/recent")
@timer
@login_required
@Validator(bad_request)
def api_v1_recent(
    time=Query(int, rules=Min(1)),
    location=Query(str, rules=MinLen(1))
):
    now = datetime.now()
    target_time = now - timedelta(seconds=time)
    model = Detection(current_app.db)
    result = model.find_detection_by_gt(location, target_time)
    if result:
        return response_200({
            'is_detected': True
        })
    return response_200({
        'is_detected': False
    })