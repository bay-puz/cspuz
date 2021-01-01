from cspuz.puzzle import util


def _encode_pzpr(n, code):
    if n < 0:
        return ''
    max = len(code) - 1
    if n > max:
        return _encode_pzpr(max, code) + _encode_pzpr(n - max, code)
    return code[n]


def _encode_0v(n):
    return _encode_pzpr(n, '0123456789abcdefghijklmnopqrstuv')


def _encode_gz(n):
    if n == 0:
        return ''
    return _encode_pzpr(n, '0ghijklmnopqrstuvwxyz')


def _encode_hex(dec):
    ad = ''
    if dec >= 16:
        ad = '-'
    return ad + hex(dec)[2:]


def _decode_pzpr(s, code):
    if len(s) > 1:
        return _decode_pzpr(s[0]) + _decode_pzpr(s[1:])
    for i in range(len(code)):
        if code[i] == s:
            return i
    return 0


def _decode_0v(s):
    return _decode_pzpr(s, '0123456789abcdefghijklmnopqrstuv')


def _decode_gz(s):
    return _decode_pzpr(s, 'ghijklmnopqrstuvwxyz') + 1


def _is_number(s):
    try:
        int(s, 16)
    except ValueError:
        return False
    return True


def to_puzz_link_ripple(height, width, problem):
    puzz_link_body = ''

    border = ''
    for y in range(height):
        for x in range(width):
            if x < width - 1:
                if problem[y][x] != problem[y][x+1]:
                    border += '1'
                else:
                    border += '0'

    i = 0
    border += '0000'
    while i + 5 <= len(border):
        dec = int(border[i:i+5], 2)
        puzz_link_body += _encode_0v(dec)
        i += 5

    border = ''
    for y in range(height):
        for x in range(width):
            if y < height - 1:
                if problem[y][x] != problem[y+1][x]:
                    border += '1'
                else:
                    border += '0'

    i = 0
    border += '0000'
    while i + 5 <= len(border):
        dec = int(border[i:i+5], 2)
        puzz_link_body += _encode_0v(dec)
        i += 5

    spaces = 0
    for y in range(height, height*2):
        for x in range(width):
            if problem[y][x] > 0:
                if spaces > 0:
                    puzz_link_body += _encode_gz(spaces)
                    spaces = 0
                puzz_link_body += _encode_hex(problem[y][x])
            else:
                spaces += 1
    if spaces > 0:
        puzz_link_body += _encode_gz(spaces)

    return 'https://puzz.link/p?ripple/{}/{}/{}'.format(height, width, puzz_link_body)


def parse_puzz_link_ripple(url):
    width, height, body = url.split('/')[-3:]
    height = int(height)
    width = int(width)

    borders_right = [[None for _ in range(width - 1)] for _ in range(height)]
    borders_down = [[None for _ in range(width)] for _ in range(height - 1)]
    numbers = [[0 for _ in range(width)] for _ in range(height)]
    pos = 0
    for s in body:
        if pos < height * (width - 1) + (height - 1) * width:
            dec = _decode_0v(s)
            border = format(dec, '0>5b')
            w = width - 1
            if pos < height * w:
                for b in border:
                    borders_right[int(pos / w)][pos % w] = bool(int(b))
                    pos += 1
                    if pos == height * w:
                        break
            elif pos < height * w + (height - 1) * width:
                for b in border:
                    pos_d = pos - (height * w)
                    borders_down[int(pos_d / width)][pos_d % width] = bool(int(b))
                    pos += 1
                    if pos == height * w + (height - 1) * width:
                        break
        else:
            p = pos - (height * (width - 1) + (height - 1) * width)
            if _is_number(s):
                numbers[int(p / width)][p % width] = int(s, 16)
                pos += 1
            else:
                pos += _decode_gz(s)

    problem = util.split_block_by_border(height, width, borders_right, borders_down) + numbers

    return height, width, problem
