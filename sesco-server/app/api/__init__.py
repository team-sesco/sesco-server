"""
API Request Handler and util
"""
import json
from flask import Flask, g, current_app, request, Response
from loguru import logger
from model.mongodb import Log


def init_app(app: Flask):

    @app.before_first_request
    def before_first_request():
        pass

    @app.before_request
    def before_request():
        if g.get('pest_dict') is None:
            with open('model/json/test.json', 'rt', encoding='UTF8') as f:
                g.pest_dict = json.load(f)

    @app.after_request
    def after_request(response):
        config = current_app.config

        # Slow API Tracking
        if (
            'process_time' in g
            and g.process_time >= config['SLOW_API_TIME']
        ):
            log_str = (
                f"\n!!! SLOW API DETECTED !!! \n"
                f"ip: {request.remote_addr}\n"
                f"url: {request.full_path}\n"
                f"input_json: {str(request.get_json())}\n"
                f"slow time: {str(g.process_time)}\n"
            )
            logger.warning(log_str)

        # API Logging
        if config['API_LOGGING']:
            if isinstance(response, Response):
                status_code = response.status_code
            else:
                status_code = response[1]

            log_documnet = {
                'ipv4': request.remote_addr,
                'url': request.full_path,
                'method': request.method,
                'params': request.data.decode(),
                'status_code': status_code
            }
            if 'user_oid' in g:
                log_documnet['user_id'] = g.user_oid
            Log(current_app.db).insert_log(log_documnet)

        # Warning Message
        if 'warn_msg' in g:
            logger.warning(
                f"\n!!! Warning Message !!!\n"
                f"ip: {request.remote_addr}\n"
                f"url: {request.full_path}\n"
                f"Content: {g.warn_msg}"
            )

        return response

    @app.teardown_request
    def teardown_request(exception):
        pass

    @app.teardown_appcontext
    def teardown_appcontext(exception):
        pass
