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
            'img': None,
            'category': None,
            'location': None,
            'model_result': None,
            'search_str': None,
            'is_deleted': False,
            'is_detected': False,
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
    def delete_detection_all(self, user_oid: ObjectId):
        return self.col.delete_many({'user_id': user_oid})

        
    def get_detections(self, user_oid: ObjectId, skip: int, limit: int):
        return list(self.col.find(
            {
                'user_id': user_oid,
                'is_deleted': False,
            }
        ).sort('created_at', DESCENDING)
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
            {'search_str': {'$regex': search_str}},
            {
                'search_str': 0
            }
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

    def get_detection_by_location(self, location:dict):
        """
        지역(location)을 받아 그 지역에 있는 탐지
        """
        location_x = float(location.get('x'))
        location_y = float(location.get('y'))
        return list(self.col.find(
            {
                'location.region_3depth_name': location.get('region_3depth_name'),
                'is_detected': True,
                '$and': [
                    {'location.x': {'$gt': location_x-0.005, '$lt': location_x+0.005}},
                    {'location.y': {'$gt': location_y-0.005, '$lt': location_y+0.005}},
                ]
            },
            {
                'model_result.name': 1,
                'location.x': 1,
                'location.y': 1,
                'img': 1
            })
        )
    
    def find_detection_by_gt(self, location:str, time: datetime):
        return list(self.col.find(
            {
                'created_at': {'$gte': time},
                'location.region_3depth_name': location
            }
        ))