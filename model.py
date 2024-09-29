import json

from app import app, api, db
from config.constant import *
from os_utils import run


@api.model("项目")
class Project(db.Model):
    def __init__(self, project_id):
        self.project_id = project_id

    def __str__(self):
        return json.dumps(self.__dict__)


@api.model("Java项目")
class JavaProject(Project):
    __tablename__ = "java_project"
    project_id = db.Column(db.Integer, primary_key=True)
    java_path = db.Column(db.String(255))
    jar_path = db.Column(db.JSON)
    config = db.Column(db.JSON)
    properties = db.Column(db.JSON)
    process = db.Column(db.Integer)

    def __init__(self, **kwargs):
        project_id = kwargs.get("project_id")
        super().__init__(project_id)
        self.java_path = kwargs.get("java_path") | DE_JAVA_PATH
        self.jar_path = {}
        self.config = {}
        self.properties = {}
        self.process = None
        self.exception = None

    def __str__(self):
        return f"Java Project {self.project_id}"

    def run(self):
        jvm_config = [f"-X{key}{value}" for key, value in self.config.items()]
        properties = [f"-D{key}={value}" for key, value in self.properties.items()]
        cmd = [self.java_path, *jvm_config, "-jar", self.jar_path, *properties]
        self.process, self.exception = run(cmd)

    def stop(self):
        if self.process:
            self.process.terminate()

    def restart(self):
        self.stop()
        self.run()

    def status(self):
        if self.process:
            return self.process.poll()
        if self.exception:
            return self.exception
        return None


@api.model("Html项目")
class HtmlProject(Project):
    def __str__(self):
        return f"Html Project {self.project_id}"


query_map = {
    "java": JavaProject.query,
    "html": HtmlProject.query
}
