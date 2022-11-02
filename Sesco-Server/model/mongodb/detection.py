from datetime import datetime
from pymongo import IndexModel, DESCENDING, ASCENDING
from bson.objectid import ObjectId
from .base import Model


class Detection(Model):

    VERSION = 1

    @property
    def index(self) -> list:
        return [
            IndexModel([('id', ASCENDING)], unique=True),
            IndexModel([('oauth_id', ASCENDING)]),
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
            'coordinate': None,
            'result': None,
            'message': None,
            'search_str':None,
            'is_deleted':False,
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
            {'$set': {'is_deleted':True}}
        )


    def get_detections(self, skip: int, limit: int):
        return list(self.col.find()
            .sort('updated_at', DESCENDING)
            .skip(skip)
            .limit(limit))
    
    def get_detection_one(self, detection_id:ObjectId):
        return self.col.find_one(
            {'_id': detection_id},
        )
    def get_search(self, search_str:str):
        """
        search_str이 정해지고나서 
        """
        pass