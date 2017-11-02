import requests
import requests_mock
from nose.tools import assert_equal
from nose.tools import assert_in
from helpers.protocols.http.client import Client as HttpClient

class TestHttpClient():

    def test_repr(self):
        client = HttpClient('enclave.framework')
        assert_equal(str(client), '<HttpClient enclave.framework:80>')

    def test_get_url_nossl_bool(self):
        client = HttpClient('enclave.framework')
        url = client._get_url('/')
        assert_equal(url[0:4], 'http')

    def test_get_url_nossl_string(self):
        client = HttpClient('enclave.framework', ssl='False')
        url = client._get_url('/')
        assert_equal(url[0:4], 'http')

    def test_get_url_ssl_bool(self):
        client = HttpClient('enclave.framework', ssl=True)
        url = client._get_url('/')
        assert_equal(url[0:5], 'https')

    def test_get_url_ssl_string(self):
        client = HttpClient('enclave.framework', ssl='True')
        url = client._get_url('/')
        assert_equal(url[0:5], 'https')

    def test_get_url_ssl_port(self):
        client = HttpClient('enclave.framework', port=443)
        url = client._get_url('/')
        assert_equal(url[0:5], 'https')

    def test_get_url_nonstandard_port(self):
        client = HttpClient('enclave.framework', port=8444)
        url = client._get_url('/')
        assert_equal(url[-5:-1], '8444')

    def test_add_headers(self):
        client = HttpClient('enclave.framework')

        # test standard 80/443
        client._set_host_header('127.0.0.1')
        assert_equal(client.headers.get('Host'), '127.0.0.1')

        # test non-standard port
        client._set_host_header('127.0.0.1:8444')
        assert_equal(client.headers.get('Host'), '127.0.0.1:8444')

        # test misc header
        client._set_other_header('X-Enclave', 'v0.1a')
        assert_in('X-Enclave', client.headers.keys())
        assert_in('v0.1a', client.headers.values())

    def test_parse_response(self):
        with requests_mock.Mocker() as mock_request:
            mock_request.get('http://http//victim.pirate:80/implant?cmd=foo', text='c:\\cwd\nnt\\system\nc:\\pwd\n')
            client = HttpClient('http://victim.pirate')
            client._request('/implant', 'get', {'cmd': 'foo'})
            cwd, pwd, contents = client._parse_response()
            assert_equal(cwd, 'c:\\cwd')
            assert_equal(pwd, 'c:\\pwd')
            assert_equal(contents, 'nt\\system')
