from app import app, api


@api.model("项目")
class Project:
    project_id = api.field("项目ID", required=True, example="1")

    def __init__(self, project_id):
        self.project_id = project_id

    def __str__(self):
        return f"Project {self.project_id}"


@api.model("Java项目")
class JavaProject(Project):
    java_path = api.field("Java路径", required=True, example="/usr/local/java")
    jar_path = api.field("Jar路径", required=True, example="/usr/local/jar")
    configure = api.field("配置", required=True)

    def __str__(self):
        return f"Java Project {self.project_id}"


@api.model("Html项目")
class HtmlProject(Project):
    def __str__(self):
        return f"Html Project {self.project_id}"
