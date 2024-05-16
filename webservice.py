#!/usr/bin/env python3
import os
import subprocess
import time
import getpass
import urllib.request


class run:
    def __init__(self, cmd, cwd=None):
        super().__init__()
        self.cmd = cmd
        self.message = ''
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        self.status, self.stdout, self.stderr = res.returncode, res.stdout.decode("utf-8"), res.stderr.decode("utf-8")

    def __str__(self):
        st = 'OK' if self.status == 0 else f'FAILED status={self.status}'
        msg = '' if self.message == '' else f'message={self.message}\n'
        return \
            f'{msg}' \
            f'status={st}\n' \
            f'command={" ".join(self.cmd)}\n' \
            f'stdout: ------------------------------\n' \
            f'{self.stdout}\n' \
            f'stderr: ------------------------------\n' \
            f'{self.stderr}'


class WebService:
    TIMEOUT_ERROR = 123

    def API_aspetta(self):
        time.sleep(3)
        return 'aspetta un po'

    def API_git_pull(self):
        return str(run(['git', 'pull']))

    def API_make_build(self):
        return str(run(['make', 'build']))

    def API_make_down(self):
        return str(run(['make', 'down']))

    def API_make_up(self):
        return str(run(['make', 'up']))

    def API_make_logs(self):
        return str(run(['make', 'logs']))

    def API_docker_compose_down(self):
        return str(run(['docker', 'compose', 'down']))
