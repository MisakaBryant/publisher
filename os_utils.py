import subprocess

import psutil

from external import log, process_pool


def run(cmd: list):
    log.info(f"Run command: {' '.join(cmd)}")
    try:
        popen = subprocess.Popen(cmd)
    except subprocess.SubprocessError as e:
        log.error(f"Run command error: {e}")
        return None, 0, str(e)
    log.info(f"Process {popen.pid} started")
    pid = popen.pid
    process = psutil.Process(pid)
    process_pool[pid] = process
    return pid, None
