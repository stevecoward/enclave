import click
from os.path import expanduser


class Logger():
    @staticmethod
    def log(message, category='default', show=True, exclude_prefix=False, spool=True):
        categories = {
            'success': {
                'prefix': '[+]',
                'fg': 'green',
            },
            'warning': {
                'prefix': '[*]',
                'fg': 'yellow',
            },
            'fail': {
                'prefix': '[!]',
                'fg': 'red',
            },
            'info': {
                'prefix': '[-]',
                'fg': 'blue',
            },
            'default': {
                'prefix': '',
                'fg': 'white',
            }
        }
        assert category in categories
        final_message = message if exclude_prefix else '%s %s' % (
            categories[category]['prefix'], message)
        if show:
            click.secho(final_message, fg=categories[category]['fg'])
        if spool:
            home_path = expanduser('~')
            with open('%s/.enclave/spool' % home_path, 'ab') as fh:
                fh.write('%s\n' % final_message)
