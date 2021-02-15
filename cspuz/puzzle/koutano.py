import sys

import cspuz
from cspuz import Solver
from cspuz.constraints import alldifferent
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D


def solve_koutano(height, width, problem):
    solver = Solver()
    col = solver.int_array(width, 0, width - 1)
    row = solver.int_array(height, 0, height - 1)

    solver.add_answer_key(col)
    solver.add_answer_key(row)

    solver.ensure(alldifferent(col))
    solver.ensure(alldifferent(row))

    for y in range(height):
        for x in range(width):
            if problem[y][x] >= 0:
                solver.ensure(col[x] + row[y] == problem[y][x])

    is_sat = solver.solve()
    return is_sat, col, row


def generate_koutano(height, width, hard=False, symmetry=False, verbose=False):
    pattern = list(range(1, height + width - 3))
    if not hard:
        pattern += [0, height + width - 2]

    def pretest(problem):
        if not hard:
            return True

        for y in range(height):
            count_hint = 0
            for x in range(width):
                count_hint += 1 if problem[y][x] > -1 else 0
            if count_hint > 2:
                return False
        for x in range(width):
            count_hint = 0
            for y in range(height):
                count_hint += 1 if problem[y][x] > -1 else 0
            if count_hint > 2:
                return False
        return True

    generated = generate_problem(lambda problem: solve_koutano(height, width, problem),
                                 builder_pattern=ArrayBuilder2D(height, width, pattern, default=-1, symmetry=symmetry, disallow_adjacent=hard),
                                 clue_penalty=lambda problem: count_non_default_values(problem, default=-1, weight=2),
                                 pretest=pretest, verbose=verbose)
    return generated


def _main():
    if len(sys.argv) == 1:
        height = 5
        width = 4
        problem = [
            [ 2, -1, -1,  3],
            [-1, -1, -1, -1],
            [-1,  7, -1, -1],
            [-1, -1,  2, -1],
            [-1,  4, -1, -1],
        ]
    else:
        height, width = map(int, sys.argv[1:])

        problem = generate_koutano(height, width, verbose=True, hard=True, symmetry=True)
        if problem is None:
            return 1

    is_sat, up, left = solve_koutano(height, width, problem)

    if not is_sat:
        print('no answer')
        return 1

    print(' ', end='  ')
    for x in range(width):
        if up[x].sol is None:
            print(' ?', end=' ')
        else:
            if up[x].sol > 10:
                print(up[x].sol, end=' ')
            else:
                print(' {}'.format(up[x].sol), end=' ')
    print('')
    print(' ', end='  ')
    for x in range(width):
        print('---', end='')
    print('')
    for y in range(height):
        if left[y].sol is None:
            print('?', end=' |')
        else:
            print(left[y].sol, end=' |')
        for x in range(width):
            if problem[y][x] >= 10:
                print(problem[y][x], end=' ')
            elif problem[y][x] >= 0:
                print(' {}'.format(problem[y][x]), end=' ')
            else:
                print(' .', end=' ')
        print('')

    return 0


if __name__ == '__main__':
    _main()
