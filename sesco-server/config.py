'''
Application Config Setting
'''
import os
from dotenv import load_dotenv

load_dotenv(verbose=True)

APP_NAME = "SESCO"
BASEDIR = os.path.abspath(os.path.dirname(__file__))
FLASK_CONFIG = os.getenv('FLASK_CONFIG') or 'development'


class Config:
    '''General Config'''
    SLOW_API_TIME = 0.5
    API_LOGGING = False
    JSON_AS_ASCII = False
    JWT_TOKEN_LOCATION = ['headers']
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 24 * 365
    JWT_REFRESH_TOKEN_EXPIRES = 60 * 24 * 365
    JWT_SESSION_COOKIE = False
    SECRET_KEY = os.environ[APP_NAME + "_SECRET_KEY"]

    # MongoDB
    MONGODB_URI = os.environ[APP_NAME + "_MONGODB_URI"]
    MONGODB_NAME = os.environ[APP_NAME + "_MONGODB_NAME"]

    # S3
    S3_DOMAIN = os.environ[APP_NAME + "_S3_DOMAIN"]
    S3_BUCKET_NAME = os.environ[APP_NAME + "_S3_BUCKET_NAME"]
    S3_ACCESS_KEY_ID = os.environ[APP_NAME + "_S3_ACCESS_KEY_ID"]
    S3_SECRET_ACCESS_KEY = os.environ[APP_NAME + "_S3_SECRET_ACCESS_KEY"]
    
    # Admin
    ADMIN_ID = os.environ[APP_NAME + '_ADMIN_ID']
    ADMIN_PW = os.environ[APP_NAME + '_ADMIN_PW']

    # AI
    AI_SERVER_DOMAIN = os.environ[APP_NAME + '_AI_SERVER_DOMAIN']
    AI_SERVER_API_KEY = os.environ[APP_NAME + '_AI_SERVER_API_KEY']

    @staticmethod
    def init_app(app):
        pass


if FLASK_CONFIG == 'development':
    class AppConfig(Config):
        DEBUG = True
        TESTING = False
        JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24 * 2
        JWT_REFRESH_TOKEN_EXPIRES = 60 * 60 * 24 * 60

elif FLASK_CONFIG == 'production':
    class AppConfig(Config):
        DEBUG = False
        TESTING = False
        SECRET_KEY = os.environ[APP_NAME + "_SECRET_KEY"]

        # Google Oauth
        GOOGLE_OAUTH_CLIENT_ID = os.environ['GOOGLE_OAUTH_CLIENT_ID']
        GOOGLE_OAUTH_CLIENT_SECRET = os.environ['GOOGLE_OAUTH_CLIENT_SECRET']
        GOOGLE_OAUTH_REDIRECT_URI = os.environ['GOOGLE_OAUTH_REDIRECT_URI']
else:
    raise Exception("Flask Config not Selected.")


config = AppConfig


class TestConfig(Config):
        DEBUG = True
        TESTING = True


if __name__ == '__main__':
    pass
