from flask import Flask, request, jsonify
from flask_restx import Api, Resource

from config.log_config import get_logger

# App 和 Api
app = Flask(__name__)
api = Api(app, version="0.1", title="Publisher", description="Auto Publisher API")

# 配置日志
log = get_logger(app)


@api.route("/project")
class ProjectController(Resource):
    @api.expect("project_id")
    def get(self):
        pid = request.args.get("project_id")
        log.info(f"Get project {pid}")
        log.debug(f"Get project {pid}")
        return {"project": "Auto Publisher " + str(pid)}

    @api.expect()
    def post(self):
        return {"new": "Auto Publisher"}


@api.route("/run")
def run():
    log.info("Run project")


@app.errorhandler(404)
def not_found(error):
    log.error(error)
    return jsonify({'message': 'Resource not found'}), 404


@app.errorhandler(500)
def server_error(error):
    log.error(error)
    return jsonify({'message': 'An internal error occurred'}), 500


if __name__ == "__main__":
    app.run(debug=True, port=9000)
