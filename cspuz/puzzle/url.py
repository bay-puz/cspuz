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


def _encode_az(n):
    if n == 0:
        return ''
    return _encode_pzpr(n, '0abcdefghijklmnopqrstuvwxyz')


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


def _decode_az(s):
    return _decode_pzpr(s, 'abcdefghijklmnopqrstuvwxyz') + 1


def _decode_p(dec, p, len=5):
    def _base_p(n):
        if n >= p:
            return str(_base_p(n//p)) + str(_base_p(n%p))
        return str(n)

    return _base_p(dec).zfill(len)


def _is_number(s, p):
    try:
        int(s, p)
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


def encode_circles_in_border(height, width, problem):
    def _encode_border(borders):
        ret = ''
        for i in range((len(borders) + 2) // 3):
            dec = 0
            for j in range(3):
                if i * 3 + j >= len(borders):
                    break
                dec += borders[i * 3 + j] * (3 ** (2 - j))
            ret += _encode_0v(dec)
        return ret

    return _encode_border(sum(problem, []))


def encode_numbers(height, width, numbers, zero_is_number=False, max_number=20):
    ret = ''
    spaces = 0
    for y in range(height):
        for x in range(width):
            if numbers[y][x] > 0 or (numbers[y][x] == 0 and zero_is_number):
                if spaces > 0:
                    ret += _encode_az(spaces) if max_number < 10 else _encode_gz(spaces)
                    spaces = 0
                ret += str(numbers[y][x]) if max_number < 10 else _encode_hex(numbers[y][x])
            else:
                spaces += 1
    if spaces > 0:
        ret += _encode_az(spaces) if max_number < 10 else _encode_gz(spaces)

    return ret


def split_puzz_link_url(puzz_link):
    width, height, body = puzz_link.split('/')[-3:]
    return int(height), int(width), body


def decode_blocks(height, width, body, is_hint_by_number=False):
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
            if _is_number(s, 16):
                numbers[p // width][p % width] = int(s, 16)
                pos += 1
            else:
                pos += _decode_gz(s)

    problem = util.split_block_by_border(height, width, borders_right, borders_down)
    if is_hint_by_number:
        problem += numbers
    return problem


def decode_circles_in_border(height, width, body):
    circles_right = [[None for _ in range(width - 1)] for _ in range(height)]
    circles_down = [[None for _ in range(width)] for _ in range(height - 1)]

    circles = ''
    for s in body:
        circles += _decode_p(_decode_0v(s), 3, 3)

    len_r = (width - 1) * height
    len_d = width * (height - 1)
    for p, c in enumerate(circles):
        if p < len_r:
            circles_right[p // (width - 1)][p % (width - 1)] = int(c)
        elif p < len_r + len_d:
            p2 = p - len_r
            circles_down[p2 // width][p2 % width] = int(c)

    return circles_right + circles_down


def decode_numbers(height, width, body):
    numbers = [[-1 for _ in range(width)] for _ in range(height)]
    pos = 0
    for s in body:
        if _is_number(s, 10):
            numbers[pos // width][pos % width] = int(s)
            pos += 1
        else:
            pos += _decode_az(s)
    return numbers
