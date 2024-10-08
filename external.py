import logging
from typing import Dict

import psutil
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
log: logging.Logger
api = Api(version="1.0", title="Publisher", description="Auto publish project")


class ProcessPool:
    """
    进程池，维护系统中的所有进程，存放 psutil.Process 实例
    """

    def __init__(self):
        self.pool: Dict[int, psutil.Process] = {}

    def get(self, pid):
        process = self.pool.get(pid)
        if not process:
            try:
                process = psutil.Process(pid)
                self.pool[pid] = process
            except psutil.NoSuchProcess:
                log.warning("No such process: pid=" + pid)
        return process

    def __getitem__(self, pid):
        return self.get(pid)

    def __setitem__(self, pid, process):
        self.pool[pid] = process

    def pop(self, pid):
        process = self.pool.get(pid)
        if process.is_running:
            process.terminate()
        return self.pool.pop(pid)


# 全局进程池
process_pool = ProcessPool()
