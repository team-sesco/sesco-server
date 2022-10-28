import traceback
from flask import Blueprint, jsonify, request


error_handler = Blueprint("error_handler", __name__)


@error_handler.app_errorhandler(400)
def bad_request(error):
    """400 Error Handler"""
    return jsonify(msg=str(error)), 400


@error_handler.app_errorhandler(404)
def not_found(error):
    """404 Error Handler"""
    return jsonify(msg=str(error)), 404


@error_handler.app_errorhandler(500)
def internal_server_error(error):
    """500 Error Handler"""
    return jsonify(msg='Internal Server Error'), 500
