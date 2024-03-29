"""
v1 API Module Package
"""
from flask import Blueprint

api_v1 = Blueprint('api_v1', __name__)

from . import user, post, detection, bookmark, help, report, notification
