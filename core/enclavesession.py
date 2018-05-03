import os
import subprocess
from datetime import datetime
from os.path import expanduser
from helpers import Logger
from core.models import database, enclave_tables

class EnclaveSession():
    def __init__(self, args={}):
        self.args = args
        home_path = expanduser('~')
        if not os.path.exists('%s/.enclave' % home_path):
            Logger.log('enclave folder doesn\'t exist, creating...',
                       'warning', spool=False)
            os.mkdir('%s/.enclave' % home_path)

        if 'bootstrap' in args and args.bootstrap:
            Logger.log('bootstrapping db...', 'success')
            database.create_tables(enclave_tables)
            for table_instance in enclave_tables:
                table = table_instance()
                table.bootstrap()

        if 'api' in args and args.api:
            Logger.log('starting enclave api server...', 'info')
            subprocess.check_output('tmux new-session -A -d -s enclave-api', shell=True)
            subprocess.check_output('tmux send-keys -t enclave-api "source env/bin/activate && export FLASK_APP=api/__init__.py" C-m', shell=True)
            subprocess.check_output('tmux send-keys -t enclave-api "flask run" C-m', shell=True)

        self.initiated = datetime.now()
        Logger.log('\n--- new enclave session initiated (%s) ------------\n' %
                   self.initiated.isoformat(), show=False)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.closing_at = datetime.now()
        time_diff = self.closing_at - self.initiated

        if 'api' in self.args and self.args.api:
            subprocess.check_output('tmux send-keys -t enclave-api "C-c" C-m', shell=True)
            subprocess.check_output('tmux send-keys -t enclave-api "exit" C-m', shell=True)

        Logger.log('exiting enclave, thanks for playing...', 'info')
        Logger.log('\n--- closing enclave session ({timestamp}) [{elapsed:.2f}s] ------------------'.format(
            timestamp=self.closing_at.isoformat(), elapsed=time_diff.total_seconds()), show=False)
