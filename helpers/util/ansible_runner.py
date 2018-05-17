import os
import re
import tempfile
import subprocess
from terminaltables import AsciiTable
from helpers.log import Logger

class AnsibleRunner():
    hosts_path = ''
    vars_path = ''

    def __init__(self, role, hosts_dict, profile=None):
        self.role = role
        self.hosts = hosts_dict
        self.vars = {}
        if profile:
            profile.properties.update({
                'profile': profile.name,
            })
            self.vars = profile.properties

    def _write(self, content):
        os_fh, temp_path = tempfile.mkstemp()
        with open(temp_path, 'w') as fh:
            fh.write(content)
        return temp_path

    def _write_hosts(self):
        hosts_string = '[{role}]\n{host} ansible_ssh_private_key_file={key_path}'.format(role=self.role, host=self.hosts['host'], key_path=self.hosts['key_path'])
        self.hosts_path = self._write(hosts_string)

    def _write_vars(self):
        vars_string = '%s%s' % ('---\n', ''.join(['{}: {}\n'.format(key, val) for key, val in self.vars.iteritems()]))
        self.vars_path = self._write(vars_string)

    def _cleanup(self):
        Logger.log('cleaning up temp files...', 'info')
        map(os.remove, [self.hosts_path, self.vars_path])

    def run(self):
        recap_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+:\s+ok=(\d+)\s+changed=(\d+)\s+unreachable=(\d+)\s+failed=(\d+)')

        self._write_hosts()
        self._write_vars()

        cmd = 'source env/bin/activate && ansible-playbook -i {hosts_path} ansible/site.yml --tags \'{role}\''.format(hosts_path=self.hosts_path, role=self.role)
        if self.vars_path:
            cmd = cmd + ' --extra-vars "@{vars_path}"'.format(vars_path=self.vars_path)

        cmd_output = subprocess.check_output(cmd, shell=True)
        Logger.log('finished deployment!', 'success')

        matches = [match.groups() for match in recap_pattern.finditer(cmd_output)]
        if not len(matches):
            Logger.log('ansible finished but the recap wasn\'t found in the output', 'warning')
            return False

        puppet_ip, ok, changed, unreachable, failed = matches[0]
        t = [
            ['puppet_ip', 'ok', 'changed', 'unreachable', 'failed'],
            [puppet_ip, ok, changed, unreachable, failed],
        ]
        table = AsciiTable(t)
        table.title = 'deploy results'
        Logger.log('')
        Logger.log(table.table, 'success', exclude_prefix=True)
        Logger.log('')

        self._cleanup()