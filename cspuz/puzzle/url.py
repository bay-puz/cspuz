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


def encode_blocks(height, width, problem):
    def _encode_border(borders):
        ret = ''
        for i in range((len(borders) + 4) // 5):
            dec = 0
            for j in range(5):
                if i * 5 + j < len(borders) and borders[i * 5 + j]:
                    dec += (2 ** (4 - j))
            ret += _encode_0v(dec)
        return ret

    border_right = []
    for y in range(height):
        for x in range(width - 1):
            border_right.append(problem[y][x] != problem[y][x+1])

    border_down = []
    for y in range(height - 1):
        for x in range(width):
            border_down.append(problem[y+1][x] != problem[y][x])

    return _encode_border(border_right) + _encode_border(border_down)


def encode_numbers(height, width, numbers, zero_is_number=False):
    ret = ''
    spaces = 0
    for y in range(height):
        for x in range(width):
            if numbers[y][x] > 0 or (numbers[y][x] == 0 and zero_is_number):
                if spaces > 0:
                    ret += _encode_gz(spaces)
                    spaces = 0
                ret += _encode_hex(numbers[y][x])
            else:
                spaces += 1
    if spaces > 0:
        ret += _encode_gz(spaces)

    return ret


def _split_puzz_link_url(puzz_link):
    width, height, body = puzz_link.split('/')[-3:]
    return int(height), int(width), body


def decode_blocks(puzz_link, is_hint_by_number=False):
    height, width, body = _split_puzz_link_url(puzz_link)

    borders_right = [[None for _ in range(width - 1)] for _ in range(height)]
    borders_down = [[None for _ in range(width)] for _ in range(height - 1)]
    if is_hint_by_number:
        numbers = [[0 for _ in range(width)] for _ in range(height)]
    pos = 0
    pos_r = (width - 1) * height
    pos_d = width * (height - 1)
    for s in body:
        if pos < pos_r + pos_d:
            dec = _decode_0v(s)
            border = format(dec, '0>5b')
            if pos < pos_r:
                for b in border:
                    borders_right[pos // (width - 1)][pos % (width - 1)] = bool(int(b))
                    pos += 1
                    if pos == pos_r:
                        break
            elif pos < pos_r + pos_d:
                for b in border:
                    p = pos - pos_r
                    borders_down[p // width][p % width] = bool(int(b))
                    pos += 1
                    if pos == pos_r + pos_d:
                        break
        elif is_hint_by_number:
            p = pos - pos_r - pos_d
            if _is_number(s):
                numbers[p // width][p % width] = int(s, 16)
                pos += 1
            else:
                pos += _decode_gz(s)

    problem = util.split_block_by_border(height, width, borders_right, borders_down)
    if is_hint_by_number:
        problem += numbers
    return height, width, problem
