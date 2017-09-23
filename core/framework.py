from helpers import Logger


class GenericOptions():
    table_data = [['name', 'setting', 'required', 'description']]

    def __init__(self):
        pass


class GenericKeywords():
    words = ['use', 'exit', 'quit']

    def __init__(self):
        pass

    def _get_keywords(self):
        return list(frozenset(self.words))


class ModuleBase(GenericKeywords):
    def __init__(self):
        GenericKeywords.__init__(self)


class GenericModuleMethods(GenericOptions):
    def __init__(self):
        GenericOptions.__init__(self)

    def _option_info(self):
        return self.table_data + self.options_info

    def _set(self, options):
        key, value = options
        option_item = next(
            (item for item in self.options_list if item['name'] == key), None)
        if len(option_item):
            option_item['value'] = value
            Logger.log('%s --> %s' % (key, value), 'success')
            self.options_info = [[option['display_name'], option['value'],
                                  option['required'], option['help']] for option in self.options_list]

    def _load_opts(self, resource_path=''):
        opts = []
        if resource_path:
            try:
                with open(resource_path, 'r') as fh:
                    opts = fh.read()
                    opts = opts.split('\n')
            except:
                Logger.log(
                    'error opening resource file. ensure you use absolute file paths...', 'fail')

            for opt in opts:
                opt_split = opt.split(' ')
                opt_value = ' '.join(opt_split[2:])
                if 'set' in opt:
                    self._set(opt_split[1:3])


class BaseModuleKeywords(GenericKeywords):
    def __init__(self):
        GenericKeywords.__init__(self)
        self.words.extend([
            'options',
            'set',
            'execute',
            'load_opts',
        ])
