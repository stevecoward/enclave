import re
from datetime import datetime
from helpers import Logger


class GenericValidator():
    value = None

    def __init__(self, value):
        self.value = value

    def _is_valid(self):
        return self.value is not None


class IntPortValidator(GenericValidator):

    def __init__(self, value):
        GenericValidator.__init__(self, value)

    def _is_valid(self):
        return 1 <= int(self.value) <= 65535


class UrlValidator(GenericValidator):

    url_pattern = re.compile(
        u'^'
        # protocol identifier
        u'(?:(?:https?|ftp)://)'
        # user:pass authentication
        u'(?:\S+(?::\S*)?@)?'
        u'(?:'
        # IP address exclusion
        # private & local networks
        u'(?!(?:10|127)(?:\.\d{1,3}){3})'
        u'(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})'
        u'(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})'
        # IP address dotted notation octets
        # excludes loopback network 0.0.0.0
        # excludes reserved space >= 224.0.0.0
        # excludes network & broadcast addresses
        # (first & last IP address of each class)
        u'(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])'
        u'(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}'
        u'(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))'
        u'|'
        # host name
        u'(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)'
        # domain name
        u'(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*'
        # TLD identifier
        u'(?:\.(?:[a-z\u00a1-\uffff]{2,}))'
        u')'
        # port number
        u'(?::\d{2,5})?'
        # resource path
        u'(?:/\S*)?'
        u'$', re.UNICODE)

    def __init__(self, value):
        GenericValidator.__init__(self, value)

    def _is_valid(self):
        return self.url_pattern.match(self.value)


class HttpMethodValidator(GenericValidator):

    def __init__(self, value):
        GenericValidator.__init__(self, value)

    def _is_valid(self):
        return self.value.upper() in ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']


class BooleanValidator(GenericValidator):

    def __init__(self, value):
        GenericValidator.__init__(self, value)

    def _is_valid(self):
        return True if self.value.upper() in ['TRUE', 'YES', 'Y', 'FALSE', 'NO', 'N'] else False


class DictStringValidator(GenericValidator):

    def __init__(self, value):
        GenericValidator.__init__(self, value)
        kv_string_pattern = re.compile('(\w+)=(\w+);?\s?')

        final_dict = {}

        for match in kv_string_pattern.findall(value):
            final_dict.update({
                match[0]: match[1],
            })

        self.value = final_dict

    def _is_valid(self):
        if isinstance(self.value, dict):
            if len(self.value):
                return True
        return False

class EnumValidator(GenericValidator):
    options = []

    def __init__(self, value, options):
        GenericValidator.__init__(self, value)
        self.options = options

    def _is_valid(self):
        return self.value in self.options


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
        required_options = [option['name'] for option in self.options_list if option['required']]
        for option_name, option_value in self._get_module_options().iteritems():
            if option_name in required_options and option_value == '':
                Logger.log('option is required: %s' % option_name, 'fail')
                is_valid = False
        return is_valid

    def _exec(self, options=''):
        if not self._validate_options():
            Logger.log('aborted exec due to invalid options', 'fail')
            return False
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
                opt_split = opt.split(' ')
                opt_var = opt_split[1]
                opt_value = ' '.join(opt_split[2:])
                if 'set' in opt:
                    self._set([opt_var, opt_value])

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
                'exiting... don\\t forget to clean up!', 'warning')
            return False
        return user_input

class EnclaveSession():
    def __init__(self):
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

class BaseModuleKeywords(GenericKeywords):
    def __init__(self):
        GenericKeywords.__init__(self)
        self.words.extend([
            'options',
            'set',
            'exec',
            'execute',
            'load_opts',
            'info',
        ])
