import re
from helpers import Logger
from core.validators import *


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
        Logger.log(self.name_ascii, 'success', exclude_prefix=True)
        GenericOptions.__init__(self)

    def _option_info(self):
        self.options = [option['name'] for option in self.options_list]
        self.options_info = [[option['display_name'], '%s...' % option['value'][:60] if len(option['value']) > 60 else option['value'],
                              option['required'], option['help']] for option in self.options_list]
        return self.table_data + self.options_info

    def _get_module_options(self):
        options = {}
        for item in self.options_list:
            options[item['name']] = item['value']
        return options

    def _validate_options(self):
        is_valid = True
        required_options = [option['name']
                            for option in self.options_list if option['required']]
        for option_name, option_value in self._get_module_options().iteritems():
            if option_name in required_options and option_value == '':
                Logger.log('option is required: %s' % option_name, 'fail')
                is_valid = False
        return is_valid

    def _exec(self, options=''):
        if not self._validate_options():
            Logger.log('aborted exec due to invalid options', 'fail')
            return False
        self.options = self._get_module_options()
        return True

    def _set(self, options):
        key, value = options
        option_item = next(
            (item for item in self.options_list if item['name'] == key), None)
        if option_item and len(option_item):
            if option_item['type'] == 'int_port':
                validator = IntPortValidator(value)
            elif option_item['type'] == 'url':
                validator = UrlValidator(value)
            elif option_item['type'] == 'http_method':
                validator = HttpMethodValidator(value)
            elif option_item['type'] == 'bool':
                validator = BooleanValidator(value)
            elif option_item['type'] == 'kv_string':
                validator = DictStringValidator(value)
            elif option_item['type'] == 'enum':
                validator = EnumValidator(value, option_item['enum_options'])
            elif option_item['type'] == 'file_path':
                validator = FilePathValidator(value)
            else:
                validator = GenericValidator(value)

            if validator._is_valid():
                option_item['value'] = value
                Logger.log('%s --> %s' % (key, value), 'success')
                self.options_info = [[option['display_name'], option['value'],
                                      option['required'], option['help']] for option in self.options_list]
            else:
                Logger.log('%s --> %s (failed validation)' %
                           (key, value), 'fail')

    def _load_opts(self, resource_path=''):
        opts = []
        if resource_path:
            try:
                with open(resource_path, 'r') as fh:
                    opts = fh.read()
                    opts = filter(None, opts.split('\n'))
            except:
                Logger.log(
                    'error opening resource file. ensure you use absolute file paths...', 'fail')

            for opt in opts:
                if opt.startswith('set'):
                    opt_split = opt.split(' ')
                    opt_var = opt_split[1]
                    opt_value = ' '.join(opt_split[2:])
                    self._set([opt_var, opt_value])
                elif opt.startswith('use'):
                    pass
                else:
                    self.call_action(opt)

    def _replace_template_vars(self, template_path, payload_options):
        template_contents = ''
        template_var_pattern = re.compile(r'({{2}\s+?([A-Za-z0-9_]+)\s+?}{2})')
        with open(template_path, 'r') as fh:
            template_contents = fh.read()

        for match in template_var_pattern.findall(template_contents):
            template_var, var_name = match

            var = self.payloads[payload_options['os']][var_name]
            template_contents = template_contents.replace(template_var, var)

        with open(template_path, 'w') as fh:
            fh.write(template_contents)

    def _get_input(self, prompt_fields):
        host, prompt = prompt_fields
        module_prompt = '[{name_short}][{host}] {prompt}> '.format(
            name_short=self.name_short, host=host, prompt=prompt)
        user_input = raw_input(module_prompt)
        Logger.log('%s %s' % (module_prompt, user_input),
                   exclude_prefix=True, show=False)
        if user_input in ['quit', 'exit']:
            Logger.log(
                'exiting... don\'t forget to clean up!', 'warning')
            return False
        return user_input


class BaseModuleKeywords(GenericKeywords):
    def __init__(self):
        GenericKeywords.__init__(self)
        self.words.extend([
            'options',
            'set',
            'exec',
            'load_opts',
            'info',
        ])
