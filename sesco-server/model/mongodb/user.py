from datetime import datetime
from pymongo import IndexModel, ASCENDING, DESCENDING
from bson.objectid import ObjectId
from .base import Model


class User(Model):

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
            'id': None,
            'password': None,
            'name': None,
            'img': None,
            'auth_type': "origin",
            'last_access_date': datetime.now(),
            'device_token': None,
            'is_deleted': False,
            'bookmarks': [],
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            '__version__': self.VERSION,
        }

    def insert_user(self, document: dict):
        """user 생성 쿼리"""
        return self.col.insert_one(self.schemize(document))

    def upsert_user(self, document: dict):
        """사용자 업설트"""
        return self.col.update_one(
            {'id': document['id']},
            {'$set': self.schemize(document)},
            upsert=True
        )
    def get_password_with_id(self, user_id: str):
        """user_id를 통한 PW 조회 쿼리"""
        return self.col.find_one(
            {'id': user_id},
            {'password': 1}
        )

    def get_password(self, user_oid: ObjectId):
        """user_oid를 통한 PW 조회 쿼리"""
        return self.col.find_one(
            {'_id': user_oid},
            {'password': 1}
        )

    def get_userinfo(self, user_oid: ObjectId):
        """user 정보 반환 쿼리"""
        return self.col.find_one(
            {'_id': user_oid}
        )
    def get_user_by_name(self, user_name: str):
        return self.col.find_one(
            {'name': user_name}
        )

    def get_userinfo_simple(self, user_oid: ObjectId):
        """user 정보 반환 쿼리 (id, name, photo만)"""
        return self.col.find_one(
            {'_id': user_oid},
            {
                'id': 1,
                'name': 1,
                'photo': 1
            }
        )

    def delete_user(self, user_oid: ObjectId):
        self.col.delete_one({'_id': user_oid})
        

    def update_user(self, user_oid: ObjectId, document: dict):
        """user 정보 갱신 쿼리"""
        return self.col.update_one(
            {'_id': user_oid},
            {'$set': {
                **document,
                'updated_at': datetime.now(),
            }}
        )

    def update_user_photo(self, user_oid: ObjectId, photo: str):
        """user 사진 갱신 쿼리"""
        self.col.update_one(
            {'_id': user_oid},
            {'$set': {
                'photo': photo,
                'updated_at': datetime.now()
            }}
        )
         
    def get_bookmarks(self, user_oid: ObjectId, limit: int):
        """
        북마크 반환
        """

        return self.col.find_one(
            {'_id': user_oid},
            {'bookmarks': {'$slice': -1 * limit} if limit else 1 }
        )
    
    def get_user_by_bookmark(self, user_oid: ObjectId, detection_id: ObjectId) -> list:
        """
        user_oid에 해당하는 북마크에 detection_id가 있는지 확인
        존재할 경우 True
        존재하지 않을 경우 False
        """
        return self.col.find_one(
            {
                "_id": user_oid,
                "bookmarks.detection_id": {"$in": [detection_id]}
            }
        )

    def upsert_bookmarks(self, user_oid: ObjectId, document: dict):
        """북마크 업설트"""
        self.col.update_one(
            {'_id': user_oid},
            {'$push': {'bookmarks': document}},
            upsert=True
        )

    def delete_bookmarks(self, user_oid: ObjectId, detection_oid: ObjectId):
        """북마크 삭제"""
        return self.col.update_one(
            {'_id': user_oid},
            {'$pull': {'bookmarks': {'detection_id': detection_oid}}}
        )

    