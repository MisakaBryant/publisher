import locale
import subprocess
from typing import Union

from external import log


def run(cmd: Union[list, str]):
    if isinstance(cmd, list):
        log.info(f"Run command: {' '.join(cmd)}")
    else:
        cmd = cmd.replace("\r", "").replace("\n", "&&")
        log.info(f"Run command: {cmd}")
    try:
        popen = subprocess.Popen(cmd, shell=True,
                                 encoding=locale.getpreferredencoding(),
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = popen.communicate()
        if stdout:
            log.info(stdout)
        if stderr:
            log.error(stderr)
    except subprocess.SubprocessError as e:
        log.exception(e)
        return None, str(e)
    return popen.pid, None
