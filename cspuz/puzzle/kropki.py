import sys

from cspuz import Solver, graph
from cspuz.constraints import alldifferent
from cspuz.puzzle import url


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


def generate_kropki(size, is_anti_knight=False):
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
    if len(sys.argv) < 3:
        puzz_link = 'https://puzz.link/p?kropki/4/4/o4c56gd6'
        if len(sys.argv) == 2:
            puzz_link = sys.argv[1]
        print('problem: {}'.format(puzz_link))
        size, problem = parse_puzz_link_kropki(puzz_link)
        is_sat, numbers = solve_kropki(size, problem)
        print('has_answer:', is_sat)
        if is_sat:
            for y in range(size):
                for x in range(size):
                    if numbers[y, x].sol is None:
                        print('？', end=' ')
                    else:
                        print(numbers[y, x].sol, end=' ')
                print('')


if __name__ == '__main__':
    _main()
