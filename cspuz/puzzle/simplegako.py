import sys

from cspuz import Solver
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D
from cspuz.puzzle import url


def solve_simplegako(height, width, problem):
    solver = Solver()
    numbers = solver.int_array((height, width), 1, height + width - 1)
    solver.add_answer_key(numbers)

    for y in range(height):
        for x in range(width):
            if problem[y][x] > 0:
                solver.ensure(numbers[y, x] == problem[y][x])

    def _count(y0, x0, n):
        sum = -1
        for y in range(height):
            sum += (numbers[y, x0] == n).cond(1, 0)
        for x in range(width):
            sum += (numbers[y0, x] == n).cond(1, 0)
        return sum

    for y in range(height):
        for x in range(width):
            solver.ensure(numbers[y, x] == _count(y, x, numbers[y, x]))

    is_sat = solver.solve()
    return is_sat, numbers


def generate_simplegako(height, width, verbose=True, disallow_adjacent=False, symmetry=False, hard=False):
    pattern = range(max(height, width) + 1) if hard else range(height + width - 1)

    def pretest(problem):
        if not hard:
            return True

        for y in range(height):
            for x in range(width):
                if problem[y][x] > 0:
                    for i in range(1, width - x):
                        if problem[y][x+i] == problem[y][x]:
                            return False
                    for i in range(1, height - y):
                        if problem[y+i][x] == problem[y][x]:
                            return False

        mean = (height + width) // 2
        count_big = 0
        for y in range(height):
            for x in range(width):
                if problem[y][x] > 2:
                    count_big += 1
        return (count_big < mean)

    generated = generate_problem(lambda problem: solve_simplegako(height, width, problem),
                                builder_pattern=ArrayBuilder2D(height, width, pattern, default=0,
                                disallow_adjacent=disallow_adjacent, symmetry=symmetry),
                                clue_penalty=lambda problem: count_non_default_values(problem, default=0, weight=5),
                                pretest=pretest, verbose=verbose)
    return generated


def to_puzz_link_simplegako(height, width, problem):
    dummy = [[0 for _ in range(width)] for _ in range(height)]
    puzz_link_body = url.encode_blocks(height, width, dummy)
    puzz_link_body += url.encode_numbers(height, width, problem, zero_is_number=False)

    puzz_link_base = 'https://puzz.link/p?ripple/v:'
    return '{}/{}/{}/{}'.format(puzz_link_base, width, height, puzz_link_body)


def parse_puzz_link_simplegako(puzz_link_url):
    height, width, body = url.split_puzz_link_url(puzz_link_url)

    problem = url.decode_blocks(height, width, body, is_hint_by_number=True)
    return height, width, problem[height:]


def _main():
    if len(sys.argv) == 1:
        problem = "https://puzz.link/p?ripple/v:/7/7/000000000000000000j1i8j4i684l21m13p1g"
        height, width, problem = parse_puzz_link_simplegako(problem)
        is_sat, answer = solve_simplegako(height, width, problem)

        if not is_sat:
            print('no answer', file=sys.stderr)
            return

        print('answer:')
        for y in range(height):
            for x in range(width):
                if answer[y, x].sol is None:
                    print('?', end=' ')
                else:
                    print(answer[y, x].sol, end=' ')
            print('')

    elif len(sys.argv) > 2:
        height, width = map(int, sys.argv[1:3])
        gen = generate_simplegako(height, width)
        if gen is None:
            print('not generated')
            return

        link = to_puzz_link_simplegako(height, width, gen)
        print('problem: {}'.format(link))

        is_sat, answer = solve_simplegako(height, width, gen)
        print('answer:')
        for y in range(height):
            for x in range(width):
                if answer[y, x].sol is None:
                    print('?', end=' ')
                else:
                    print(answer[y, x].sol, end=' ')
            print('')


if __name__ == '__main__':
    _main()
