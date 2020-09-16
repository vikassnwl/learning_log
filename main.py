import re

def markdown(s):

    # regex_pre = re.compile(r'(.*)')
    # s = regex_pre.sub(r'<pre>\1</pre>', s)

    # handling spaces
    regex_space = re.compile(r'(\s)')
    s = regex_space.sub(r'&nbsp;', s)

    # markdown for bold text
    regex_bold = re.compile(r'\*([^*]+)\*')
    s = regex_bold.sub(r'<b>\1</b>', s)

    # markdown for italic text
    regex_italic = re.compile(r'\_([^_]+)\_')
    s = regex_italic.sub(r'<i>\1</i>', s)

    # markdown for heading
    regex_italic = re.compile(r'# ([\w\s]+)')
    s = regex_italic.sub(r'<h1>\1</h1>', s)

    return s.replace('\n', '<br>')
