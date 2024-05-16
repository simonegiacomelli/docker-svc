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
    port_start = 6001
    port_count = 5
    ports = list(range(port_start, port_start+port_count))
    marker = "marker-melinda"
    pcmd_regex= f'^[^lxterminal].*{marker}'
    pkill_base_args = ['-u', getpass.getuser(), '-f', pcmd_regex]
    pgrep_base_args = ['-a'] + pkill_base_args 
    
    def API_update(self):
        for name, cmd in [('git pull', self.git_pull)
            , ('compila melinda', self.compile_melinda)
            , ('compila melinda_web', self.compile_melinda_web)
                          ]:
            result = cmd()
            if result.status != 0:
                result.message = f'update fallito nell\'operazione [{name}]'
                return str(result)

        return f'update ha eseguito melinda\n\n' + self.API_run_melinda_forzato()

    def compile_melinda(self) -> run:
        return run(['./compile-melinda.sh'])

    def API_compile_melinda(self):
        return str(self.compile_melinda())

    def compile_melinda_web(self) -> run:
        return run(['./compile-melinda-web.sh'])

    def API_compile_melinda_web(self):
        return str(self.compile_melinda_web())

    def API_run_melinda(self):
        res = self.pgrep_processes()
        if res.status == 0:
            res.message = 'melinda era gia'' in esecuzione'
        else:
            res = 'melinda non era in esecuzione.\n\n' + self.API_run_melinda_forzato()            

        return str(res)

    def API_run_melinda_forzato(self):
        pkill_res = self.pkill_processes()
        if pkill_res.status == self.TIMEOUT_ERROR:
            return str(pkill_res)
        base_args = ['./melinda', self.marker]
        def new(args):
            res = subprocess.Popen(['nohup', 'lxterminal', '-e'] + base_args + args, cwd="..", stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, preexec_fn=os.setpgrp)

            return res

        def new_melinda(port):
            res = new(['-mergeargs', 'mergeargs_server_web.txt', '-port', f'{port}'])
            time.sleep(0.1)
            return res

        pid_list = [new_melinda(port).pid for port in self.ports]

        mailer_pid = new(['-mergeargs', 'mergeargs_mailer.txt']).pid

        result = f'melinda_pid={pid_list}\nmailer_pid{mailer_pid}'
        return result

    def API_aspetta(self):
        time.sleep(3)
        return 'aspetta un po'

    def API_verifica_vitalita(self):
        ok = []
        failed = []
        for port in self.ports:
            port = str(port)
            try:
                decode = urllib.request.urlopen(f'http://localhost:{port}/alive', timeout=1).read().decode('utf-8')
                ok.append(port + ' ' + decode.strip())
            except Exception as ex:
                failed.append(port + ' ' + str(ex))

        ok_lines = '\n'.join(ok)
        failed_lines = '\n'.join(failed)
        res = ''
        if len(failed) > 0:
            res += f'Ci sono dei processi non vitali:\n{failed_lines}\n\n'
            
        if len(ok) == 0:
            res = 'Attenzione! Nessun processo di melinda risulta vitale!\n\n' + res
        else:
            res += f'Processi vitali:\n\n{ok_lines}'

        return res
    
    def git_pull(self):
        return run(['git', 'pull'], cwd='..')

    def API_git_pull(self):
        return str(self.git_pull())

    def API_pkill_melinda(self):
        return str(self.pkill_processes())
    
    def API_pgrep_melinda(self):
        return str(self.pgrep_processes())

    def pkill_processes(self) -> run:        
        pkill_result = run(['pkill'] + self.pkill_base_args)
        timeout = 8.0 # in seconds
        sleeps = 0.25
        for retry in range(int(timeout/sleeps)):
            grep_result = self.pgrep_processes()
            if grep_result.status == 0:
                print('Waiting for melinda to exit...')
                time.sleep(0.25)
            else:
                pkill_result.message = f'Kill melinda eseguito con successo (retry={retry})'
                return pkill_result
        grep_result.status = self.TIMEOUT_ERROR
        grep_result.message = 'Kill melinda fallito. Timeout nell''attesa' 
        return grep_result

    def pgrep_processes(self) -> run:
        res = run(['pgrep'] + self.pgrep_base_args)
        if res.status != 0:
            res.message = 'processi di melinda non trovati!'
        return res

if __name__ == '__main__':
    # git_pull()
    # compile_melinda()
    svc = WebService()
    pid = svc.API_run_melinda()
    time.sleep(1.0)
    # os.kill(pid, signal.SIGINT)
    # os.kill(pid, signal.SIGTERM)
    # os.kill(pid, signal.SIGKILL)
    # os.kill(pid, signal.SIGQUIT)
    # os.kill(pid, signal.SIGABRT)
