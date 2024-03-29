import sys
import argparse
from os.path import expanduser
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from terminaltables import AsciiTable

from helpers import Logger, chunks
from core import ModuleBase
from core import EnclaveWordCompleter
from core import EnclaveSession

from modules import load_module

parser = argparse.ArgumentParser(description='enclave')
parser.add_argument('-api', action='store_true',
                    help='toggle api server at runtime')
parser.add_argument('-bootstrap', action='store_true',
                    help='initialize database and table data')
args = parser.parse_args()


Logger.log("""                     .__                                   
  ____   ____   ____ |  | _____ ___  __ ____               
_/ __ \ /    \_/ ___\|  | \__  \\  \/ // __ \              
\  ___/|   |  \  \___|  |__/ __ \\   /\  ___/              
 \___  >___|  /\___  >____(____  /\_/  \___  >   .___      
     \/     \/     \/          \/    _____ \/  __| _/__  __
                              ______ \__  \   / __ |\  \/ /
                             /_____/  / __ \_/ /_/ | \   / 
                                     (____  /\____ |  \_/  
                                          \/      \/       """, 'fail', exclude_prefix=True, spool=False)


home_path = expanduser('~')
session = EnclaveSession(args)
module = ModuleBase()
action = ''

while True:
    Logger.log('', exclude_prefix=True)
    prompt_text = u'enclave> ' if action == '' else u'enclave:%s> ' % action
    user_input = prompt(prompt_text,
                        history=FileHistory(
                            '%s/.enclave/history.txt' % home_path),
                        auto_suggest=AutoSuggestFromHistory(),
                        completer=EnclaveWordCompleter(module, WORD=True),
                        )

    Logger.log('%s%s' % (prompt_text, user_input),
               show=False, exclude_prefix=True)

    if user_input in ['exit', 'quit']:
        session.close()
        sys.exit(0)

    if 'back' in user_input:
        action = ''

    elif 'use' in user_input:
        action = user_input.lstrip('use')
        module = load_module(action)

    elif 'set' in user_input and action != '':
        module._set(filter(None, user_input.lstrip('set').split(' ')))

    elif 'exec' in user_input:
        module._exec(user_input)

    elif 'load_opts' in user_input and action != '':
        module._load_opts(user_input.lstrip('load_opts '))

    elif 'options' in user_input:
        table = AsciiTable(module._option_info())
        table.title = 'options'
        Logger.log(module.name_ascii, 'success', exclude_prefix=True)
        Logger.log(table.table, 'success', exclude_prefix=True)

    elif 'info' in user_input:
        Logger.log(module.name_ascii, exclude_prefix=True)
        Logger.log('     - %s' % module.author, exclude_prefix=True)
        Logger.log('', exclude_prefix=True)
        Logger.log('', exclude_prefix=True)
        Logger.log('module name:', exclude_prefix=True)
        Logger.log('     %s' % module.name, exclude_prefix=True)
        Logger.log('', exclude_prefix=True)
        Logger.log('description:', exclude_prefix=True)
        for chunk in chunks(module.description, 60):
            Logger.log('     %s' % chunk.lstrip(' '), exclude_prefix=True)
        Logger.log('', exclude_prefix=True)
        Logger.log('options:', exclude_prefix=True)
        Logger.log('     %s' % ' | '.join(
            [option['name'] for option in module.options_list if option['required']]), exclude_prefix=True)

    elif len(filter(None, [user_input.startswith(x) for x in module.words])):
        module.call_action(user_input)

    elif '42' in user_input:
        from pprint import pprint; import ipdb; ipdb.set_trace()
        x = None
