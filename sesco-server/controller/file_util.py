"""
# 각 파일 객체 명세
file: Flask's FileStorage
img: PIL's Image
bytesio: BytesIO
"""
from uuid import uuid4
from io import BytesIO
from typing import List, Optional
from PIL import Image
import boto3
from controller.s3 import S3Controller, make_path
from werkzeug.datastructures import FileStorage


def extract_ext(origin_filename: str):
    return origin_filename.rsplit('.', 1)[1].lower()


def file_to_img(file: FileStorage) -> Image:
    bytes_io = BytesIO(file.stream.read())
    return Image.open(bytes_io)


def img_to_bytesio(img: Image) -> BytesIO:
    img_file = BytesIO()
    img.save(img_file, format=img.format)
    img_file.seek(0)
    return img_file


def resize_img(img: Image, width: int, height: int):
    # TODO: 추후 프론트와 파일 사이즈 회의 후 결정
    w, h = img.size
    if width < w or height < h:
        resized_img = img.resize((width, height))
        resized_img.format = img.format
        return resized_img
    else:
        return img


def upload_to_s3(
    s3: S3Controller,
    files: List[FileStorage],
    type: str,
    object_id: str,
) -> str:
    """
    # 복수의 파일 리스트를 s3에 업로드하고 오브젝트 path list 반환
    저장 경로: {type-path}/{identifier}/{index}.{ext}
    - 주의: object_id는 반드시 각 콘텐츠별 고유한 값을 가져야 함.
    """
    result = []
    for file in files:
        ext = extract_ext(file.filename)
        filename = f"{object_id}.{ext}"
        object_path = make_path(type, filename)
        uploaded_uri = s3.upload_fileobj(
            file, object_path,
            extra={
                'ACL': 'public-read',
                'ContentType': file.content_type,
            }
        )
        result.append(uploaded_uri)
    return result
