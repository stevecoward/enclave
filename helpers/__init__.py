from log import Logger
from http import build_url, make_request, parse_implant_response
from string import normalize_line_endings

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]