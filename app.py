from logging.config import dictConfig

from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy

from config.log_config import log_config
from model import Project, JavaProject, query_map

# App 和 Api
app = Flask(__name__)
api = Api(app, version="0.1", title="Publisher", description="Auto Publisher API")

# 加载日志配置
dictConfig(log_config)
log = app.logger

# 加载 sqlite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////sqlite/database.db'
db = SQLAlchemy(app)


@api.route("/project")
class ProjectController(Resource):
    @api.expect("project_id")
    def get(self):
        pid = request.args.get("project_id")
        log.info(f"Get project {pid}")
        project_type = request.args.get("type")
        project = query_map[project_type].filter_by(project_id=pid).first()
        return jsonify({
            "code": 200,
            "msg": "success",
            "data": str(project)
        })

    @api.expect()
    def post(self):
        body = request.json
        log.info(f"Create project {body}")
        project = Project(**body)
        db.session.add(project)
        return jsonify({
            "code": 200,
            "msg": "success",
            "data": project.project_id
        })


@api.route("/list_project")
def list_project():
    log.info("List all projects")
    project_type = request.args.get("type")
    projects = query_map[project_type].all()
    return jsonify({
        "code": 200,
        "msg": "success",
        "data": [str(project) for project in projects]
    })


@api.route("/run", methods=["POST"])
def run():
    project_id = request.args.get("project_id")
    log.info(f"Run project {project_id}")
    project = Project.query.filter_by(project_id=project_id).first()
    if project is JavaProject:
        project.run()
    return jsonify({
        "code": 200,
        "msg": "success"
    })


@app.errorhandler(404)
def not_found(error):
    log.error(error)
    return jsonify({
        "code": 404,
        "msg": "Not Found"
    }), 404


@app.errorhandler(500)
def server_error(error):
    log.error(error)
    return jsonify({
        "code": 500,
        "msg": "Server Error"
    }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
