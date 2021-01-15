import sys

from random import randint
from cspuz import Solver, graph
from cspuz.constraints import alldifferent
from cspuz.puzzle import url, util


def solve_kropki(size, problem, is_anti_knight=False):
    solver = Solver()

    numbers = solver.int_array((size, size), 1, size)
    solver.add_answer_key(numbers)

    for i in range(size):
        solver.ensure(alldifferent(numbers[i, :]))
        solver.ensure(alldifferent(numbers[:, i]))

    def _numbers_consecutive(y1, x1, y2, x2):
        solver.ensure((numbers[y1, x1] + 1 == numbers[y2, x2]) | (numbers[y1, x1] - 1 == numbers[y2, x2]))

    def _numbers_not_consecutive(y1, x1, y2, x2):
        solver.ensure(numbers[y1, x1] + 1 != numbers[y2, x2])
        solver.ensure(numbers[y1, x1] - 1 != numbers[y2, x2])

    def _numbers_double(y1, x1, y2, x2):
        solver.ensure((numbers[y1, x1] + numbers[y1, x1] == numbers[y2, x2]) | (numbers[y1, x1] == numbers[y2, x2] + numbers[y2, x2]))

    def _numbers_not_double(y1, x1, y2, x2):
        solver.ensure(numbers[y1, x1] + numbers[y1, x1] != numbers[y2, x2])
        solver.ensure(numbers[y1, x1] != numbers[y2, x2] + numbers[y2, x2])

    for y in range(size):
        for x in range(size - 1):
            if problem[y][x] == 1:
                _numbers_consecutive(y, x, y, x+1)
            elif problem[y][x] == 2:
                _numbers_double(y, x, y, x+1)
            else:
                _numbers_not_consecutive(y, x, y, x+1)
                _numbers_not_double(y, x, y, x+1)

    for y in range(size - 1):
        for x in range(size):
            if problem[y+size][x] == 1:
                _numbers_consecutive(y, x, y+1, x)
            elif problem[y+size][x] == 2:
                _numbers_double(y, x, y+1, x)
            else:
                _numbers_not_consecutive(y, x, y+1, x)
                _numbers_not_double(y, x, y+1, x)

    if is_anti_knight:
        graph.numbers_anti_knight(solver, numbers)

    is_sat = solver.solve()

    return is_sat, numbers


def _is_solved(size, answer):
    for y in range(size):
        for x in range(size):
            if answer[y, x].sol is None:
                return False
    return True


def _set_circles_on_latin(size, latin):
    problem = [[0 for _ in range(size-1)] for _ in range(size)]
    problem += [[0 for _ in range(size)] for _ in range(size-1)]

    for y in range(size):
        for x in range(size):
            n1 = latin[y][x]
            if x < size - 1:
                n2 = latin[y][x+1]
                if n1 + n2 == 3:
                    problem[y][x] = randint(1, 2)
                elif n1 == n2 + 1 or n1 + 1 == n2:
                    problem[y][x] = 1
                elif n1 == n2 * 2 or n1 * 2 == n2:
                    problem[y][x] = 2
            if y < size - 1:
                n2 = latin[y+1][x]
                if n1 + n2 == 3:
                    problem[y+size][x] = randint(1, 2)
                elif n1 == n2 + 1 or n1 + 1 == n2:
                    problem[y+size][x] = 1
                elif n1 == n2 * 2 or n1 * 2 == n2:
                    problem[y+size][x] = 2

    return problem


def generate_kropki(size, is_anti_knight=False, limit=100):
    for _ in range(limit):
        latin = util.generate_latin_square(size, is_anti_knight)
        problem = _set_circles_on_latin(size, latin)

        if is_anti_knight:
            is_sat, answer = solve_kropki(size, problem, is_anti_knight=False)
            if _is_solved(size, answer):
                continue

        is_sat, answer = solve_kropki(size, problem, is_anti_knight)
        if is_sat and _is_solved(size, answer):
            return problem

    return None


def to_puzz_link_kropki(size, problem, variant=False):
    puzz_link_base = 'https://puzz.link/p?kropki'
    if variant:
        puzz_link_base += '/v:'
    return '{}/{}/{}/{}'.format(puzz_link_base, size, size, url.encode_circles_in_border(size, size, problem))


def parse_puzz_link_kropki(puzz_link_url):
    size, _, body = url.split_puzz_link_url(puzz_link_url)
    return size, url.decode_circles_in_border(size, size, body)


def _main():
    if len(sys.argv) == 1:
        puzz_link = 'https://puzz.link/p?kropki/4/4/o4c56gd6'
        print('problem: {}'.format(puzz_link))
        size, problem = parse_puzz_link_kropki(puzz_link)
    elif len(sys.argv[1]) > 2:
        puzz_link = sys.argv[1]
        is_anti_knight = len(sys.argv) > 2
        size, problem = parse_puzz_link_kropki(puzz_link, is_anti_knight)
    else:
        size = int(sys.argv[1])
        is_anti_knight = len(sys.argv) > 2
        problem = generate_kropki(size, is_anti_knight)
        print('problem: {}'.format(to_puzz_link_kropki(size, problem, is_anti_knight)))

    is_sat, numbers = solve_kropki(size, problem, is_anti_knight)
    print('has_answer:', is_sat)
    if is_sat:
        for y in range(size):
            for x in range(size):
                if numbers[y, x].sol is None:
                    print('?', end=' ')
                else:
                    print(numbers[y, x].sol, end=' ')
            print('')


if __name__ == '__main__':
    _main()
