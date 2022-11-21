from datetime import datetime
from pymongo import IndexModel, DESCENDING, ASCENDING
from bson.objectid import ObjectId
from .base import Model


class Detection(Model):

    VERSION = 1

    @property
    def index(self) -> list:
        return [
            IndexModel([('id', ASCENDING)], unique=True)
        ]

    @property
    def schema(self) -> dict:
        return {
            'user_name': None,
            'user_img': None,
            'user_id': None,
            'name': None,
            'img': None,
            'category': None,
            'location': None,
            'model_predict': None,
            'message': None,
            'search_str': None,
            'is_deleted': False,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            '__version__': self.VERSION,
        }

    def insert_detection(self, document: dict):
        return self.col.insert_one(self.schemize(document))

    def delete_detection(self, detection_id:ObjectId):
        """탐지 기록 임시 삭제 """
        return self.col.update_one(
            {'_id': detection_id},
            {'$set': {'is_deleted': True}}
        )

    def get_detections(self, user_oid: ObjectId, skip: int, limit: int):
        return list(self.col.find(
            {
                'user_id': user_oid,
                'is_deleted': False,
            }
        ).sort('updated_at', DESCENDING)
        .skip(skip)
        .limit(limit)
    )
    
    def get_detection_one(self, detection_id: ObjectId):
        return self.col.find_one(
            {
                '_id': detection_id,
                'is_deleted': False
            },
        )

    def get_search(self, search_str: str):
        """
        검색.
        """
        return list(self.col.find(
            {'search_str': {'$regex': search_str}}
        ))

    def upsert_one(self, document: dict):
        return self.col.update_one(
            {'_id': document['_id']},
            {'$set': document},
            upsert=True
        )

    def update_user(self, user_oid: ObjectId, document: dict):
        """user 정보 갱신 쿼리"""
        return self.col.update_many(
            {'user_id': user_oid},
            {'$set': {
                **document,
                'updated_at': datetime.now(),
            }}
        )
