from datetime import datetime
from pymongo import IndexModel, DESCENDING, ASCENDING
from .base import Model


class Log(Model):

    VERSION = 1

    @property
    def index(self) -> list:
        return [
            IndexModel([('created_at', ASCENDING)])
        ]

    @property
    def api_log_schema(self) -> dict:
        return {
            'ipv4': None,
            'url': None,
            'method': None,
            'params': None,
            'status_code': None,
            'user_id': None,
            'created_at': datetime.now(),
            '__version__': self.VERSION,
        }

    @property
    def photo_upload_log_schema(self) -> dict:
        return {
            'type': 'photo_upload',
            'user_id': None,
            'photos': None,
            'created_at': datetime.now(),
            '__version__': self.VERSION,
        }

    def api_log_schemize(self, document: dict) -> dict:
        return {**self.api_log_schema, **document}

    def photo_upload_log_schemize(self, document: dict) -> dict:
        return {**self.photo_upload_log_schema, **document}

    def insert_log(self, document):
        self.col.insert_one(self.api_log_schemize(document))

    def insert_photo_upload_log(self, document):
        self.col.insert_one(self.photo_upload_log_schemize(document))

    def get_log(self, _skip: int, _limit: int):
        return list(
            self.col.find(
                {}, {
                '_id': 1,
                'ipv4': 1,
                'url': 1,
                'method': 1,
                'params': 1,
                'status_code': 1,
                'created_at': 1,
            })
            .sort([('created_at', DESCENDING)])
            .skip(_skip)
            .limit(_limit)
        )