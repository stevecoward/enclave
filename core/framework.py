import re
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
    u'$'
    , re.UNICODE)

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
            else:
                validator = GenericValidator(value)

            if validator._is_valid():
                option_item['value'] = value
                Logger.log('%s --> %s' % (key, value), 'success')
                self.options_info = [[option['display_name'], option['value'],
                                      option['required'], option['help']] for option in self.options_list]
            else:
                Logger.log('%s --> %s (failed validation)' % (key, value), 'fail')

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
                opt_var = opt_split[1]
                opt_value = ' '.join(opt_split[2:])
                if 'set' in opt:
                    self._set([opt_var, opt_value])


class BaseModuleKeywords(GenericKeywords):
    def __init__(self):
        GenericKeywords.__init__(self)
        self.words.extend([
            'options',
            'set',
            'execute',
            'load_opts',
            'info',
        ])
