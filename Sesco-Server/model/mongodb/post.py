from datetime import datetime
from pymongo import IndexModel, DESCENDING, ASCENDING
from bson.objectid import ObjectId
from .base import Model


class Post(Model):

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
            'name': None,
            'author_id': None,
            'author_name': None,
            'author_img': None,
            'files': None,
            'type': None,
            'content': None,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            '__version__': self.VERSION,
        }

    def insert_post(self, document: dict):
        return self.col.insert_one(self.schemize(document))

    def get_post_one(self, post_oid: ObjectId):
        return self.col.find_one(
            {'_id': post_oid},
        )

    def get_posts(self, skip: int, limit: int):
        return list((
            self.col.find()
            .sort('updated_at', DESCENDING)
            .skip(skip)
            .limit(limit)
        ))

    def update_post(self, post_oid: ObjectId, document: dict):
        return self.col.update_one(
            {'_id': post_oid},
            {'$set': document}
        )

    def delete_post(self, post_oid: ObjectId):
        return self.col.delete_one(
            {'_id': post_oid}
        )