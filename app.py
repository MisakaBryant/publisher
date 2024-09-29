import os
from logging.config import dictConfig

from flask import Flask, jsonify

from config.log_config import log_config
import external

# App 和 Api
app = Flask(__name__)
external.api.init_app(app)

# 加载日志配置
dictConfig(log_config)
external.log = app.logger

# 加载 sqlite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///publisher.db'
external.db.init_app(app)

# 加载路由
import api


@app.errorhandler(404)
def not_found(error):
    external.log.error(error)
    return jsonify({
        "code": 404,
        "msg": "Not Found",
        "data": str(error)
    }), 404


@app.errorhandler(500)
def server_error(error):
    external.log.error(error)
    return jsonify({
        "code": 500,
        "msg": "Server Error",
        "data": str(error)
    }), 500


if __name__ == "__main__":
    external.db.drop_all()
    external.db.create_all()
    app.run(debug=True, host="localhost", port=5000)
