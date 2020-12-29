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
    return _decode_pzpr(s, '0ghijklmnopqrstuvwxyz')


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

    for y in range(height):
        for x in range(width):
            if y < height - 1:
                if problem[y][x] != problem[y+1][x]:
                    border += '1'
                else:
                    border += '0'

    i = 0
    border += '0000'
    while i + 5 < len(border):
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
    height, width, body = url.split('/')[-3:]
    height = int(height)
    width = int(width)

    problem = [[None for _ in range(width)] for _ in range(height)]
    problem += [[0 for _ in range(width)] for _ in range(height)]
    borders_right = [[0 for _ in range(width - 1)] for _ in range(height)]
    borders_down = [[0 for _ in range(width)] for _ in range(height - 1)]
    pos = 0
    for s in body:
        if pos < height * (width - 1) + (height - 1) * width:
            dec = _decode_0v(s)
            border = format(dec, '0>5b')
            for b in border:
                if pos < height * (width - 1):
                    w = width - 1
                    borders_right[int(pos / w)][pos % w] = bool(int(b))
                else:
                    pos_d = pos - (height * (width - 1))
                    borders_down[int(pos_d / width)][pos % width] = bool(int(b))
                pos += 1
        else:
            p = pos - (height * (width - 1) + (height - 1) * width)
            if s.isdecimal():
                problem[int(p / width) + height][p % width] = int(s)
                pos += 1
            else:
                pos += _decode_gz(s)

    same_block = []
    for y in range(height):
        for x in range(width):
            if x < width - 1 and not borders_right[y][x]:
                same_block.append(([y, x], [y, x+1]))
            if y < height - 1 and not borders_down[y][x]:
                same_block.append(([y, x], [y+1, x]))

    block = 0
    for y in range(height):
        for x in range(width):
            if problem[y][x] is None:
                problem = _set_block(y, x, block, same_block, problem)
                block += 1

    return height, width, block, problem


def _set_block(y, x, block_id, same_block_list, problem):
    problem[y][x] = block_id
    for a, b in same_block_list:
        if a == [y, x] and problem[b[0]][b[1]] is None:
            problem[b[0]][b[1]] = block_id
            problem = _set_block(b[0], b[1], block_id, same_block_list, problem)
        if b == [y, x] and problem[a[0]][a[1]] is None:
            problem[a[0]][a[1]] = block_id
            problem = _set_block(a[0], a[1], block_id, same_block_list, problem)
    return problem
