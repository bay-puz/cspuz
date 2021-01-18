import sys

from cspuz import Solver, alldifferent
from cspuz.generator import generate_problem, count_non_default_values, Choice


def solve_amarune(height, width, problem):
    solver = Solver()
    numbers = solver.int_array((height, width), 1, height * width)
    solver.add_answer_key(numbers)

    solver.ensure(alldifferent(numbers))

    for y in range(height):
        for x in range(width-1):
            solver.ensure(numbers[y, x] > numbers[y, x+1])

    for y in range(height):
        for x in range(width):
            if problem[y][x] > 0:
                solver.ensure(numbers[y, x] == problem[y][x])

    for y in range(height):
        for x in range(width-1):
            for i in range(height*width):
                if problem[y+height][x] in [0, 1, 2]:
                    solver.ensure((numbers[y, x+1] == i).then(numbers[y, x] % i == problem[y+height][x]))
                elif problem[y+height][x] == 3:
                    solver.ensure((numbers[y, x+1] == i).then(numbers[y, x] % i >= 3))

    for y in range(height-1):
        for x in range(width):
            for i in range(height*width):
                if problem[y+height*2][x] in [0, 1, 2]:
                    solver.ensure(((numbers[y, x] > numbers[y+1, x]) & (numbers[y+1, x] == i)).then(numbers[y, x] % i == problem[y+height*2][x]))
                    solver.ensure(((numbers[y+1, x] > numbers[y, x]) & (numbers[y, x] == i)).then(numbers[y+1, x] % i == problem[y+height*2][x]))
                elif problem[y+height*2][x] == 3:
                    solver.ensure(((numbers[y, x] > numbers[y+1, x]) & (numbers[y+1, x] == i)).then(numbers[y, x] % i >= 3))
                    solver.ensure(((numbers[y+1, x] > numbers[y, x]) & (numbers[y, x] == i)).then(numbers[y+1, x] % i >= 3))

    is_sat = solver.solve()
    return is_sat, numbers


def generate_amarune(height, width, verbose=True):
    pattern = []
    cand = Choice([-1] + list(range(1, height * width - 1)), -1)
    pattern += [[cand for _ in range(width)] for _ in range(height)]
    cand = Choice([-1, 0, 1, 2, 3], -1)
    pattern += [[cand for _ in range(width-1)] for _ in range(height)]
    pattern += [[cand for _ in range(width)] for _ in range(height-1)]

    def pretest(problem):
        count_number_hint = 0
        for y in range(height):
            for x in range(width):
                if problem[y][x] > 0:
                    count_number_hint += 1
        return (count_number_hint < 3)

    generated = generate_problem(lambda problem: solve_amarune(height, width, problem),
                                 builder_pattern=pattern,
                                 clue_penalty=lambda problem: count_non_default_values(problem, default=-1, weight=2),
                                 pretest=pretest,
                                 verbose=verbose)
    return generated


def _main():
    if len(sys.argv) == 1:
        # https://puzsq.jp/main/puzzle_play.php?pid=2866
        height = 3
        width = 5
        problem = [
            [ 0,  0,  7,  0,  0],
            [ 0,  0,  0,  0,  0],
            [ 0,  9,  0,  0,  0],
            [-1,  0, -1,  1],
            [-1,  1, -1, -1],
            [ 3,  0, -1, -1],
            [ 2, -1, -1, -1,  2],
            [-1, -1, -1,  0, -1],
        ]

        is_sat, answer = solve_amarune(height, width, problem)

        if not is_sat:
            print('no answer', file=sys.stderr)
            return

        print('answer:')
        for y in range(height):
            for x in range(width):
                if answer[y, x].sol is None:
                    print('?', end=' ')
                else:
                    if answer[y, x].sol < 10:
                        print(' ', end='')
                    print(answer[y, x].sol, end=' ')
            print('')

    elif len(sys.argv) > 2:
        height, width = map(int, sys.argv[1:3])
        gen = generate_amarune(height, width)
        if gen is None:
            print('not generated')
            return
        for row in gen:
            for c in row:
                if c == -1:
                    print('-', end=' ')
                else:
                    print(c, end=' ')
            print('')

        is_sat, answer = solve_amarune(height, width, gen)
        for y in range(height):
            for x in range(width):
                if answer[y, x].sol is None:
                    print('?', end=' ')
                else:
                    if answer[y, x].sol < 10:
                        print(' ', end='')
                    print(answer[y, x].sol, end=' ')
            print('')


if __name__ == '__main__':
    _main()
