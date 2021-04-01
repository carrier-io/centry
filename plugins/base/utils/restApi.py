from flask_restful import Resource


class RestResource(Resource):
    def __init__(self):
        from flask import current_app
        self.logger = current_app.logger
        self.rpc = current_app.config["CONTEXT"].rpc_manager.call
