from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
log = None
api = Api(version="1.0", title="Publisher", description="Auto publish project")
