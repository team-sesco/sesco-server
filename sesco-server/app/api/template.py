"""
Template Example API
"""
from flask import Blueprint

template = Blueprint('template', __name__)


@template.route('/')
def index():
    return "<h1>Welcome to SESCO.</h1>"

