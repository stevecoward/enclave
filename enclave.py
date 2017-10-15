import sys
import os
from os.path import expanduser
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from terminaltables import AsciiTable
from datetime import datetime

from helpers import Logger, chunks
from core import ModuleBase
from core import EnclaveWordCompleter

from modules import load_module

Logger.log("""                     .__                      
  ____   ____   ____ |  | _____ ___  __ ____  
_/ __ \ /    \_/ ___\|  | \__  \\\\  \/ _/ __ \ 
\  ___/|   |  \  \___|  |__/ __ \\\\   /\  ___/ 
 \___  |___|  /\___  |____(____  /\_/  \___ >
     \/     \/     \/          \/          \/ 
                        
                        - a felux and syph0n jawn
""", 'success', exclude_prefix=True, spool=False)


home_path = expanduser('~')
if not os.path.exists('%s/.enclave' % home_path):
    Logger.log('enclave folder doesn\'t exist, creating...',
               'warning', spool=False)
    os.mkdir('%s/.enclave' % home_path)

initiated = datetime.now()
Logger.log('\n--- new enclave session initiated (%s) ------------' %
           initiated.isoformat(), show=False)

action = ''
module = ModuleBase()

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
        closing_at = datetime.now()
        time_diff = closing_at - initiated
        Logger.log('exiting enclave, thanks for playing...', 'info')
        Logger.log('\n--- closing enclave session ({timestamp}) [{elapsed:.2f}s] ------------------'.format(
            timestamp=closing_at.isoformat(), elapsed=time_diff.total_seconds()), show=False)
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
