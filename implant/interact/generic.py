from models import BaseModuleKeywords, GenericModuleMethods


class GenericImplant(BaseModuleKeywords, GenericModuleMethods):
    options_list = [{
        'name': 'host',
        'display_name': 'host',
        'value': '',
        'required': True,
        'help': 'the ip address or hostname of the target'
    }, {
        'name': 'port',
        'display_name': 'port',
        'value': '',
        'required': True,
        'help': 'the target port',
    }, {
        'name': 'path',
        'display_name': 'path',
        'value': '',
        'required': True,
        'help': 'the full path to where the shell file is located',
    }, {
        'name': 'method',
        'display_name': 'method',
        'value': '',
        'required': True,
        'help': 'http method to use when communicating with an implant',
    }, {
        'name': 'shell',
        'display_name': 'shell',
        'value': '',
        'required': True,
        'help': 'the name of the shell, example: shell.asp',
    }, {
        'name': 'ssl',
        'display_name': 'ssl',
        'value': '',
        'required': True,
        'help': 'connect to the implant using ssl',
    }, {
        'name': 'cookie',
        'display_name': 'cookie',
        'value': '',
        'required': True,
        'help': 'cookies to send',
    }, {
        'name': 'os',
        'display_name': 'os',
        'value': '',
        'required': True,
        'help': 'target operating system (win|linux)',
    }]

    def __init__(self):
        BaseModuleKeywords.__init__(self)
        GenericModuleMethods.__init__(self)
        self.options = [option['name'] for option in self.options_list]
        self.options_info = [[option['display_name'], option['value'],
                              option['required'], option['help']] for option in self.options_list]
