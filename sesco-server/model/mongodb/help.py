from datetime import datetime
from pymongo import IndexModel, DESCENDING, ASCENDING
from bson.objectid import ObjectId
from .base import Model


class Help(Model):

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
            'user_id': None,
            'user_name': None,
            'user_img': None,
            'imgs': None,
            'content': None,
            'status': "pending",  # pending, complete
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            '__version__': self.VERSION,
        }

    def insert_help(self, document: dict):
        return self.col.insert_one(self.schemize(document))

    def get_helps(self, status: str, skip: int, limit: int):
        return list((
            self.col.find(
                {'status': status} if status else {},
            )
            .sort('updated_at', DESCENDING)
            .skip(skip)
            .limit(limit)
        ))

    def get_help_one(self, help_oid: ObjectId):
        return self.col.find_one(
            {'_id': help_oid},
        )

    def update_help(self, help_oid: ObjectId, document: dict):
        return self.col.update_one(
            {'_id': help_oid},
            {'$set': document}
        )

    def delete_help(self, post_oid: ObjectId):
        return self.col.delete_one(
            {'_id': post_oid}
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
