from flask import request, jsonify
from flask_restx import Resource
from werkzeug.datastructures import FileStorage

from config.constant import DE_FILE_PATH
from external import api
from external import log, db
from model import project_map, JavaProject

project_namespace = api.namespace("project", description="Project operations", path="/api")


@project_namespace.route("/project")
class ProjectController(Resource):
    @api.expect("type", "project_id")
    def get(self):
        pid = request.args.get("project_id")
        log.info(f"Get project {pid}")
        project_type = request.args.get("type")
        project = project_map[project_type].query.filter_by(project_id=pid).first()
        return jsonify({
            "code": 200,
            "msg": "success",
            "data": str(project)
        })

    @api.expect("project_type")
    def post(self):
        project_type = request.args.get("project_type")
        body = request.json
        log.info(f"Create project {body}")
        project = project_map[project_type](**body)
        db.session.add(project)
        return jsonify({
            "code": 200,
            "msg": "success",
            "data": project.project_id
        })

    @api.expect("project_type", "project_id")
    def put(self):
        project_type = request.args.get("project_type")
        project_id = request.args.get("project_id")
        body = request.json
        log.info(f"Update project {body}")
        project = project_map[project_type].query.filter_by(project_id=project_id).first()
        for key, value in body.items():
            setattr(project, key, value)
        db.session.commit()
        return jsonify({
            "code": 200,
            "msg": "success"
        })


@project_namespace.route("/list_project")
class ListProjectController(Resource):
    @api.expect("project_type")
    def get(self):
        log.info("List all projects")
        project_type = request.args.get("project_type")
        projects = project_map[project_type].query.all()
        return jsonify({
            "code": 200,
            "msg": "success",
            "data": [str(project) for project in projects]
        })


@project_namespace.route("/run")
class RunProjectController(Resource):
    @api.expect("type", "project_id", "cmd")
    def post(self):
        project_type = request.args.get("type")
        project_id = request.args.get("project_id")
        cmd = request.args.get("cmd")
        log.info(f"Run project {project_id}")
        project = project_map[project_type].query.filter_by(project_id=project_id).first()
        if project is JavaProject:
            if cmd == "run":
                project.run()
            elif cmd == "stop":
                project.stop()
            elif cmd == "restart":
                project.restart()
            else:
                return jsonify({
                    "code": 400,
                    "msg": "cmd not support"
                }), 400
        return jsonify({
            "code": 200,
            "msg": "success"
        })


upload_parser = api.parser()
upload_parser.add_argument("file", location="files", type=FileStorage, required=True)
upload_parser.add_argument("project_type", type=str, required=True)
upload_parser.add_argument("project_id", type=int, required=True)


@project_namespace.route("/file")
class FileController(Resource):
    @api.expect(upload_parser)
    def post(self):
        args = upload_parser.parse_args()
        file = args["file"]
        project_type = args["project_type"]
        project_id = args["project_id"]
        log.info(f"Upload file {file.filename} for project {project_id}")
        file.save(DE_FILE_PATH + file.filename)
        project = project_map[project_type].query.filter_by(project_id=project_id).first()
        if project and project.add_file(DE_FILE_PATH + file.filename):
            return jsonify({
                "code": 200,
                "msg": "success"
            })
        return jsonify({
            "code": 500,
            "msg": "check if project exists or jar path is set"
        })
