import subprocess
from app import log


def run(cmd: list):
    log.info(f"Run command: {' '.join(cmd)}")
    try:
        process = subprocess.Popen(cmd)
    except subprocess.SubprocessError as e:
        log.error(f"Run command error: {e}")
        return None, e
    log.info(f"Process {process.pid} started")
    return process, None
