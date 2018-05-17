import re
import os


class GenericValidator():
    value = None

    def __init__(self, value):
        self.value = value

    def _is_valid(self):
        return self.value is not None

class FilePathValidator(GenericValidator):

    def __init__(self, value):
        GenericValidator.__init__(self, value)

    def _is_valid(self):
        return True if os.path.exists(self.value) else False


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
