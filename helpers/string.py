EOL_UNIX = '\n'
EOL_WINDOWS = '\r\n'
EOL_MAC = '\r'


def normalize_line_endings(lines, line_ending='unix'):
    lines = lines.replace(EOL_WINDOWS, EOL_UNIX).replace(EOL_MAC, EOL_UNIX)
    if line_ending == 'windows':
        lines = lines.replace(EOL_UNIX, EOL_WINDOWS)
    elif line_ending == 'mac':
        lines = lines.replace(EOL_UNIX, EOL_MAC)
    return lines
