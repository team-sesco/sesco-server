from flask import g, current_app, request
from flask_validation_extended import Validator
from app.api.response import response_200
from app.api.response import bad_request
from app.api.decorator import login_required, timer
from controller.file_util import upload_to_s3
from . import api_v1 as api

@api.post("/upload")
@timer
@login_required
@Validator(bad_request)
def api_v1_image_upload():
    """ 이미지 업로드 """
    img = request.files['img']
    
    return response_200(
        upload_to_s3(
            s3=current_app.s3,
            file=img,
            type="detection",
            object_id=g.user_oid
        )
    )
