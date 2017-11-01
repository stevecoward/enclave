import requests
from helpers.string import normalize_line_endings

requests.packages.urllib3.disable_warnings()


class Client():
    headers = {}
    cookies = {}
    user_agent = 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'

    def __repr__(self):
        return '<HttpClient {hostname}:{port}'.format(hostname=self.hostname, port=self.port)

    def __init__(self, host, port=80, ssl=False, proxies={}, username='', password=''):
        self.host = host
        self.port = port
        self.ssl = ssl
        self.proxies = proxies
        self.username = username
        self.password = password
        self.session = requests.Session()

    def _get_url(self, uri):
        prefix = 'http://'
        if self.port == 443 or eval(self.ssl):
            prefix = 'https://'
        return '{prefix}{host}:{port}{uri}'.format(prefix=prefix, host=self.host, port=self.port, uri=uri)

    def _request(self, uri, method, payload):
        self.response = None
        if method.lower() == 'get':
            self.response = self.session.get(self._get_url(uri), headers=self.headers, params=payload, cookies=self.cookies)
        elif method.lower() == 'post':
            self.response = self.session.post(self._get_url(uri), headers=self.headers, data=payload, cookies=self.cookies, proxies={'http': 'http://127.0.0.1:8080'})
        else:
            Logger.log('invalid request method used, re-check your settings and try again', 'fail')

        if not self.response or not self.response.ok:
            Logger.log('got an error making request to target %s' % url, 'fail')

    def _set_cookie_header(self, cookies):
        self.cookies = cookies

    def _set_host_header(self, value):
        self.headers.update({
            'Host': value if self.port not in [80, 443] else '%s:%s' % (self.value, self.port),
        })

    def _set_useragent_header(self, value):
        self.headers.update({
            'User-Agent': value,
        })

    def _set_auth_header(self, value):
        self.headers.update({
            'Authorization': value
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
