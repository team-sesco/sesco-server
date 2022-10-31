from datetime import datetime
from pymongo import IndexModel, DESCENDING, ASCENDING
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
            'firebase_token': None,
            'is_deleted': False,
            'bookmarks': [],
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            '__version__': self.VERSION,
        }

    def insert_user(self, document: dict):
        """user 생성 쿼리"""
        return self.col.insert_one(self.schemize(document))

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
         
    def get_bookmarks(self, user_oid:ObjectId):
        """북마크 반환"""
        return (
            list(self.col.find_one(
                {'_id':user_oid},
                {'bookmarks'}
            )
        ))
        
    def update_bookmarks(self, user_oid:ObjectId, bookmarks_list:list):
        """북마크 업데이트"""
        self.col.update_one(
            {'_id': user_oid},
            {'$set':{'bookmarks' : bookmarks_list}}
        )
    def upsert_bookmarks(self, user_oid:ObjectId, detection_oid:ObjectId):
        """북마크 업설트"""
        self.col.update_one(
            {'_id':user_oid},
            {'$push': {'detected_id': detection_oid}},
            upsert=True
        )