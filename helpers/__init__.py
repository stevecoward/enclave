from log import Logger
from http import parse_implant_response, WebRequest
from tomcat import Tomcat
from string import normalize_line_endings
from helpers.util.ansible_runner import AnsibleRunner


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
