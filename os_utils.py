import subprocess
from external import log, process_pool


def run(cmd: list):
    log.info(f"Run command: {' '.join(cmd)}")
    try:
        process = subprocess.Popen(cmd)
    except subprocess.SubprocessError as e:
        log.error(f"Run command error: {e}")
        return None, 0, str(e)
    log.info(f"Process {process.pid} started")
    pid = process.pid
    process_pool[pid] = process
    return pid, None
