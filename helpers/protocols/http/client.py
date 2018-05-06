import requests
from helpers.log import Logger
from helpers.string import normalize_line_endings

requests.packages.urllib3.disable_warnings()


class Client():
    def __init__(self, host, port, uri='/', ssl=False, debug=False):
        self.headers = {}
        self.host = host
        self.port = port
        self.uri = uri
        self.ssl = True if (ssl == True or port == 443) else ssl
        self.cookies = {}
        self.proxies = {
            'https': 'https://127.0.0.1:8080',
            'http': 'http://127.0.0.1:8080',
        } if debug else {}
        self.session = requests.Session()
        self._build_url(self.uri)

    def __repr__(self):
        return '<HttpClient {hostname}:{port}{uri}>'.format(hostname=self.host, port=self.port, uri=self.uri)

    def _build_url(self, uri):
        prefix = 'https://' if self.ssl else 'http://'
        self.url = '{prefix}{host}:{port}{uri}'.format(
            prefix=prefix, host=self.host, port=self.port, uri=uri)
        return self.url

    def _handle_response(self, response):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            Logger.log('received error {status_code} making a request to target {uri}'.format(
                status_code=e.response.status_code, uri=self.uri), 'fail')
        finally:
            self.response = (response.status_code,
                             normalize_line_endings(response.content))
        return self.response

    def set_header(self, key, value):
        self.headers.update({
            '{}'.format(key.capitalize()): value,
        })

    def get(self, uri, params={}):
        return self._handle_response(self.session.get(self._build_url(uri), params=params, headers=self.headers, cookies=self.cookies, proxies=self.proxies, verify=False))

    def post(self, uri, params={}, content_type='form'):
        if content_type == 'form':
            return self._handle_response(self.session.post(self._build_url(uri), params=params, headers=self.headers, cookies=self.cookies, proxies=self.proxies, verify=False))
        elif content_type == 'json':
            return self._handle_response(self.session.post(self._build_url(uri), json=params, headers=self.headers, cookies=self.cookies, proxies=self.proxies, verify=False))

    def delete(self, uri, params={}):
        return self._handle_response(self.session.delete(self._build_url(uri), params=params, headers=self.headers, cookies=self.cookies, proxies=self.proxies, verify=False))


class Client2():
    headers = {}
    cookies = {}
    user_agent = 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'

    def __repr__(self):
        return '<HttpClient {hostname}:{port}>'.format(hostname=self.host, port=self.port)

    def __init__(self, host, port=80, ssl=False, proxies={}, username='', password=''):
        self.host = host
        self.port = port
        self.ssl = ssl
        self.proxies = proxies
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.proxies = {
            # 'https': 'https://127.0.0.1:8080',
            # 'http': 'http://127.0.0.1:8080',
        }

    def _get_url(self, uri):
        prefix = 'http://'
        is_ssl = self.ssl if isinstance(self.ssl, bool) else eval(self.ssl)
        if self.port == 443 or is_ssl:
            prefix = 'https://'
        return '{prefix}{host}:{port}{uri}'.format(prefix=prefix, host=self.host, port=self.port, uri=uri)

    def _request(self, uri, method, payload, payload_type=''):
        self.response = None
        if method.lower() == 'get':
            self.response = self.session.get(self._get_url(
                uri), headers=self.headers, params=payload, cookies=self.cookies, proxies=self.proxies, verify=False)
        elif method.lower() == 'post':
            if payload_type == 'json':
                self.response = self.session.post(self._get_url(
                    uri), headers=self.headers, json=payload, cookies=self.cookies, proxies=self.proxies, verify=False)
            else:
                self.response = self.session.post(self._get_url(
                    uri), headers=self.headers, params=payload, cookies=self.cookies, proxies=self.proxies, verify=False)
        else:
            Logger.log(
                'invalid request method used, re-check your settings and try again', 'fail')

        if not self.response or not self.response.ok:
            Logger.log('got an error making request to target %s' %
                       uri, 'fail')

    def _set_cookie_header(self, cookies):
        self.cookies = cookies

    def _set_host_header(self, value):
        self.headers.update({
            'Host': value if self.port in [80, 443] else '%s:%s' % (value, self.port),
        })

    def _set_useragent_header(self, value):
        self.headers.update({
            'User-Agent': value,
        })

    def _set_auth_header(self, value):
        self.headers.update({
            'Authorization': 'Bearer {}'.format(value)
        })

    def _set_connection_header(self, value):
        self.headers.update({
            'Connection': value,
        })

    def _set_contenttype_header(self, value):
        self.headers.update({
            'Content-Type': value,
        })

    def _set_contentlen_header(self, value):
        self.headers.update({
            'Content-Length': value,
        })

    def _set_other_header(self, key, value):
        self.headers.update({
            key: value,
        })

    def _parse_response(self):
        response = normalize_line_endings(self.response.content)
        response_split = filter(None, response.split('\n'))
        cwd, pwd = response_split[0], response_split[-1]
        contents = '\n'.join(response_split[1:-1])
        return (cwd, pwd, contents)
