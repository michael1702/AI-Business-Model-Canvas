import logging, json
from flask import request

def setup_logging(app):
    logging.basicConfig(level=logging.INFO)
    @app.before_request
    def _log_in():
        app.logger.info(json.dumps({"evt":"request_in","path":request.path,"method":request.method}))
    @app.after_request
    def _log_out(resp):
        app.logger.info(json.dumps({"evt":"request_out","status":resp.status_code}))
        return resp
