from six import string_types
from prompt_toolkit.completion import Completer, Completion


class EnclaveWordCompleter(Completer):
    def __init__(self, module, WORD=False):
        self.module = module
        self.words = module._get_keywords()
        self.WORD = WORD
        assert all(isinstance(word, string_types) for word in self.words)

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor(WORD=self.WORD)
        if word_before_cursor == 'use':
            self.words = [
                'implant/build/generic',
                'implant/interact/generic',
                'implant/interact/slowcheetah',
                'implant/interact/asplant',
                'tomcat/foolishtom',
                'puppet/touch',
            ]
        elif word_before_cursor == 'set':
            self.words = self.module.options

        if (document.text.startswith('set') and len(document.text.split(' ')) > 2) or \
                (document.text.startswith('load_opts') and len(document.text.split(' ')) > 1):
            self.words = []

        for word in self.words:
            yield Completion(word, -len(word_before_cursor))
