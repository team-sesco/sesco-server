"""
Admin API Module Package
"""
from flask import Blueprint

api_admin = Blueprint('api_admin', __name__)

from . import auth
