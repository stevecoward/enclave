import os
from datetime import datetime
from os.path import expanduser
from helpers import Logger


class EnclaveSession():
    def __init__(self):
        home_path = expanduser('~')
        if not os.path.exists('%s/.enclave' % home_path):
            Logger.log('enclave folder doesn\'t exist, creating...',
                       'warning', spool=False)
            os.mkdir('%s/.enclave' % home_path)

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
        Logger.log('exiting enclave, thanks for playing...', 'info')
        Logger.log('\n--- closing enclave session ({timestamp}) [{elapsed:.2f}s] ------------------'.format(
            timestamp=self.closing_at.isoformat(), elapsed=time_diff.total_seconds()), show=False)
