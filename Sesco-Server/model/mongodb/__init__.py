from pymongo import MongoClient
from config import config
# Collections
from .log import Log
from .master_config import MasterConfig
from .user import User
from .post import Post
from .detection import Detection
from .help import Help
from .report import Report
from .notification import Notification
MODELS = [
    Log, MasterConfig, User, Post, Detection, Help, Report, Notification
]


def get_cursor(uri=config.MONGODB_URI) -> MongoClient:
    """Get MongoDB Cursor"""
    return MongoClient(uri, connect=False)


class ModelInitializer:

    def __init__(self):
        self.uri = config.MONGODB_URI
        self.db = config.MONGODB_NAME

    @property
    def cursor(self):
        return get_cursor(self.uri)

    def init_model(self):
        """Initializer All Process"""
        with self.cursor as cur:
            self.init_index(cur)
            self.init_author(cur)
            self.init_hello(cur)
            # self.init_tags(cur) FIXME Deprecated

    @staticmethod
    def init_index(cur):
        """Create Indexes each Collection"""
        for model in MODELS:
            model(cur).create_index()

    @staticmethod
    def init_author(cur):
        """Insert Author config"""
        MasterConfig(cur).insert_author('SESCO')

    @staticmethod
    def init_hello(cur):
        """Customize for you"""
