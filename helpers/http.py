import re
import requests
from helpers import Logger
from helpers.string import normalize_line_endings

requests.packages.urllib3.disable_warnings()

def build_url(host, port, ssl, path):
    prefix = 'http://'
    if int(port) == 443 or eval(ssl):
        prefix = 'https://'
    return '{prefix}{host}:{port}{path}'.format(prefix=prefix, host=host, port=port, path=path)

def make_request(url, method, headers, payload, cookies):
    req = None
    method = method.upper()
    cookies = cookie_string_to_dict(cookies)
    proxies = {
        'http': 'http://127.0.0.1:8080',
    }
    try:
        if method == 'GET':
            req = requests.get(url, headers=headers, params=payload, cookies=cookies)
        elif method == 'POST':
            req = requests.post(url, headers=headers, data=payload, cookies=cookies, verify=False)
        else:
            Logger.log('invalid request method used, re-check your settings and try again', 'fail')
    except:
        pass

    if not req or not req.ok:
        Logger.log('got an error making request to target %s' % url, 'fail')
        return False

    return req

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