import shutil
from datetime import datetime

from config.constant import *
from external import db
from os_utils import run


class Project(db.Model):
    __abstract__ = True

    def add_file(self, file_path):
        pass


class JavaProject(Project):
    __tablename__ = "java_project"
    project_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    java_path = db.Column(db.String(255))
    jar_path = db.Column(db.String(255))
    jars = db.Column(db.JSON)
    config = db.Column(db.JSON)
    properties = db.Column(db.JSON)
    process = db.Column(db.JSON)
    exception = db.Column(db.String(255))

    def __init__(self, **kwargs):
        self.java_path = kwargs.get("java_path", DE_JAVA_PATH)
        self.jar_path = kwargs.get("jar_path", DE_FILE_PATH)
        self.jars = []
        self.config = kwargs.get("config", {})
        self.properties = kwargs.get("properties", {})
        self.process = None
        self.exception = None

    def dict(self):
        status = 0
        if self.process:
            status = 1
            if self.process.poll():
                status = 2 if self.process.poll() == 0 else 3
        return {
            "project_id": self.project_id,
            "java_path": self.java_path,
            "jar_path": self.jar_path,
            "jars": self.jars,
            "config": self.config,
            "properties": self.properties,
            "status": status,
            "exception": self.exception or "未知异常，请查看日志" if status == 3 else None
        }

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

    def add_file(self, file_path):
        jar_name = str(self.project_id) + "-" + datetime.now().strftime("%Y%m%d%H%M%S") + ".jar"
        jar_path = self.jar_path
        if not jar_path:
            return False
        if len(self.jars) >= MAX_FILE_COUNT:
            try:
                shutil.rmtree(jar_path + self.jars.pop(MAX_FILE_COUNT - 1))
            except FileNotFoundError:
                pass
        self.jars.insert(0, jar_name)
        shutil.move(file_path, jar_path + "/" + jar_name)
        return True

    def del_all_files(self):
        for jar in self.jars:
            try:
                shutil.rmtree(self.jar_path + jar)
            except FileNotFoundError:
                pass
        self.jars.clear()


class WebProject(Project):
    __tablename__ = "web_project"
    project_id = db.Column(db.Integer, primary_key=True)

    def __str__(self):
        return f"Web Project {self.project_id}"


project_map = {
    "java": JavaProject,
    "web": WebProject
}
