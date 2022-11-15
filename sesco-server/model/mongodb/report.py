from datetime import datetime
from pymongo import IndexModel, DESCENDING, ASCENDING
from bson.objectid import ObjectId
from .base import Model


class Report(Model):

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
            'target_id': None,
            'user_id': None,
            'type': None,
            'content': None,
            'status': "pending",  # pending, complete
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            '__version__': self.VERSION,
        }

    def insert_report(self, document: dict):
        return self.col.insert_one(self.schemize(document))
    
    def get_reports(self, status: str, skip: int, limit: int):
        return list((
            self.col.find(
                {'status': status} if status else {},
            )
            .sort('updated_at', DESCENDING)
            .skip(skip)
            .limit(limit)
        ))
    
    def get_report_one(self, report_oid: ObjectId):
        return self.col.find_one(
            {'_id': report_oid},
        )

    def delete_report(self, report_oid: ObjectId):
        return self.col.delete_one(
            {'_id': report_oid}
        )

    def update_report(self, report_oid:ObjectId, document: dict):
        return self.col.update_one(
            {'_id': report_oid},
            {'$set': document}
        )