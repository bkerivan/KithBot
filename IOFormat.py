class TextFormats:
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    BLACK_BG = '\033[40m'
    RED_BG = '\033[41m'
    GREEN_BG = '\033[42m'
    YELLOW_BG = '\033[43m'
    BLUE_BG = '\033[44m'
    MAGENTA_BG = '\033[45m'
    CYAN_BG = '\033[46m'
    WHITE_BG = '\033[47m'
    BRIGHT_BLACK_BG = '\033[100m'
    BRIGHT_RED_BG = '\033[101m'
    BRIGHT_GREEN_BG = '\033[102m'
    BRIGHT_YELLOW_BG = '\033[103m'
    BRIGHT_BLUE_BG = '\033[104m'
    BRIGHT_MAGENTA_BG = '\033[105m'
    BRIGHT_CYAN_BG = '\033[106m'
    BRIGHT_WHITE_BG = '\033[107m'

class InvalidIOFormatStringError(Exception):
    pass

def colorize(text, *fmt):
    s = ""
    fmt_count = len(fmt)
    delim_count = text.count("$") - text.count("\$")
    if delim_count % 2 or fmt_count != delim_count / 2:
        raise InvalidIOFormatStringError
    start = 0
    end = -1
    for i in range(fmt_count):
        start = text.index("$", end + 1)
        if start:
            while text[start - 1] == "\\":
                start = text.index("$", start + 1)
        s += text[end + 1:start].replace("\$", "$")
        end = text.index("$", start + 1)
        while text[end - 1] == "\\":
            end = text.index("$", end + 1)
        s += "{}{}{}".format(fmt[i], text[start + 1:end].replace("\$", "$"),
                             TextFormats.ENDC)
    s += text[end + 1:]
    return s

