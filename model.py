import os
import shutil
from datetime import datetime

from config.constant import *
from external import db, process_pool
from os_utils import run


class Project(db.Model):
    __abstract__ = True

    def add_file(self, file_path):
        pass

    def del_all_files(self):
        pass


class JavaProject(Project):
    __tablename__ = "java_project"
    project_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_name = db.Column(db.String(255))
    java_path = db.Column(db.String(255))
    jar_path = db.Column(db.String(255))
    jars = db.Column(db.JSON)
    config = db.Column(db.JSON)
    properties = db.Column(db.JSON)
    pid = db.Column(db.Integer)
    exception = db.Column(db.String(255))

    def __init__(self, **kwargs):
        self.project_name = kwargs.get("project_name", "")
        self.java_path = kwargs.get("java_path", DE_JAVA_PATH)
        self.jar_path = kwargs.get("jar_path", "")
        self.jars = []
        self.config = kwargs.get("config", {})
        self.properties = kwargs.get("properties", {})
        self.pid = None
        self.exception = None

    def dict(self):
        return {
            "project_id": str(self.project_id),
            "project_name": self.project_name,
            "java_path": self.java_path,
            "jar_path": self.jar_path,
            "jars": self.jars,
            "config": self.config,
            "properties": self.properties,
            "status": self.get_status(),
            "exception": self.exception
        }

    def run(self, idx=0):
        self.stop()
        if self.pid:
            process_pool.pop(self.pid)
        jvm_config = [f"-X{key}{value}" for key, value in self.config.items()]
        properties = [f"-D{key}={value}" for key, value in self.properties.items()]
        cmd = [self.java_path + "/java", *jvm_config, "-jar", self.jar_path + "/" + self.jars[idx], *properties]
        self.pid, self.exception = run(cmd)

    def stop(self):
        if self.pid:
            process = process_pool[self.pid]
            if process.poll() is None:
                process.terminate()

    def restart(self):
        self.stop()
        self.run()

    def get_status(self):
        status = 0
        if self.pid:
            status = 1
            process = process_pool[self.pid]
            if process.poll() is not None:
                status = 2 if process.poll() == 0 else 3
        return status

    def add_file(self, file_path):
        jar_name = str(self.project_id) + "-" + datetime.now().strftime("%Y%m%d%H%M%S") + ".jar"
        jar_path = self.jar_path
        if not jar_path:
            return False
        if len(self.jars) >= MAX_FILE_COUNT:
            try:
                os.remove(jar_path + "/" + self.jars.pop(MAX_FILE_COUNT - 1))
            except FileNotFoundError:
                pass
        self.jars.insert(0, jar_name)
        if not os.path.exists(jar_path):
            os.makedirs(jar_path)
        shutil.move(file_path, jar_path + "/" + jar_name)
        return True

    def del_all_files(self):
        for jar in self.jars:
            try:
                os.remove(self.jar_path + "/" + jar)
            except FileNotFoundError:
                pass
        shutil.rmtree(self.jar_path)
        self.jars.clear()


class WebProject(Project):
    __tablename__ = "web_project"
    project_id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(255))
    zip_path = db.Column(db.String(255))
    zips = db.Column(db.JSON)
    dist_path = db.Column(db.String(255))
    status = db.Column(db.Integer)

    def __init__(self, **kwargs):
        self.project_name = kwargs.get("project_name", "")
        self.zip_path = kwargs.get("dist_path", DE_FILE_PATH)
        self.zips = []
        self.dist_path = kwargs.get("dist_path", "")
        self.status = 0

    def dict(self):
        return {
            "project_id": str(self.project_id),
            "project_name": self.project_name,
            "zip_path": self.zip_path,
            "zips": self.zips,
            "dist_path": self.dist_path,
            "status": self.status
        }

    def deploy(self, idx=0):
        zip_name = self.zips[idx]
        zip_path = self.zip_path + "/" + zip_name
        dist_path = self.dist_path
        if not dist_path:
            return False
        if not os.path.exists(dist_path):
            os.makedirs(dist_path)
        shutil.unpack_archive(zip_path, dist_path)
        self.status = 1
        return True

    def undeploy(self):
        dist_path = self.dist_path
        if os.path.exists(dist_path):
            shutil.rmtree(dist_path)
        self.status = 0

    def add_file(self, file_path):
        zip_name = str(self.project_id) + "-" + datetime.now().strftime("%Y%m%d%H%M%S") + ".zip"
        zip_path = self.zip_path
        if not zip_path:
            return False
        if len(self.zips) >= MAX_FILE_COUNT:
            try:
                os.remove(zip_path + "/" + self.zips.pop(MAX_FILE_COUNT - 1))
            except FileNotFoundError:
                pass
        self.zips.insert(0, zip_name)
        if not os.path.exists(zip_path):
            os.makedirs(zip_path)
        shutil.move(file_path, zip_path + "/" + zip_name)
        return True

    def del_all_files(self):
        for z in self.zips:
            try:
                os.remove(self.zip_path + "/" + z)
            except FileNotFoundError:
                pass
        shutil.rmtree(self.zip_path)
        self.zips.clear()


project_map = {
    "java": JavaProject,
    "web": WebProject
}
