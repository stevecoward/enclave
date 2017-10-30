import re
import requests
from helpers import Logger
from helpers.string import normalize_line_endings

requests.packages.urllib3.disable_warnings()


class WebRequest():
    def __init__(self):
        self.session = requests.Session()

    @staticmethod
    def build_url(host, port, ssl, path):
        prefix = 'http://'
        if int(port) == 443 or eval(ssl):
            prefix = 'https://'
        return '{prefix}{host}:{port}{path}'.format(prefix=prefix, host=host, port=port, path=path)

    def make_request(self, url, method, headers, payload, cookies):
        cookies = cookie_string_to_dict(cookies) if len(cookies) else {}
        response = None
        if method.lower() == 'get':
            response = self.session.get(
                url, headers=headers, params=payload, cookies=cookies)
        elif method.lower() == 'post':
            response = self.session.post(
                url, headers=headers, data=payload, cookies=cookies)
        else:
            Logger.log(
                'invalid request method used, re-check your settings and try again', 'fail')
            return response

        if not response or not response.ok:
            Logger.log('got an error making request to target %s' %
                       url, 'fail')
            return False

        return response


def cookie_string_to_dict(cookie_string):
    kv_string_pattern = re.compile('(\w+)=(\w+);?\s?')

    final_dict = {}

    for match in kv_string_pattern.findall(cookie_string):
        final_dict.update({
            match[0]: match[1],
        })

    return final_dict


def parse_implant_response(content):
    response = normalize_line_endings(content)
    response_split = filter(None, response.split('\n'))
    cwd, pwd = response_split[0], response_split[-1]
    contents = '\n'.join(response_split[1:-1])
    return (cwd, pwd, contents)
