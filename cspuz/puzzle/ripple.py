import sys

from cspuz import Solver, alldifferent


def solve_ripple(height, width, block_num, problem):
    solver = Solver()
    numbers = solver.int_array((height, width), 1, height * width + 1)
    solver.add_answer_key(numbers)

    blocks = [[] for _ in range(block_num)]
    for y in range(height):
        for x in range(width):
            blocks[problem[y][x]].append([y, x])
            if problem[y + height][x] > 0:
                solver.ensure(numbers[y, x] == problem[y + height][x])

    for block in blocks:
        solver.ensure(alldifferent([numbers[y, x] for y, x in block]))
        for y, x in block:
            solver.ensure(numbers[y, x] <= len(block))

    for y in range(height):
        for x in range(width):
            for i in range(1, width - x):
                solver.ensure((numbers[y, x] == numbers[y, x+i]).then(numbers[y, x] < i))
            for i in range(1, height - y):
                solver.ensure((numbers[y, x] == numbers[y+i, x]).then(numbers[y, x] < i))

    is_sat = solver.solve()
    return is_sat, numbers


def _main():
    # http://pzv.jp/p.html?ripple/6/6/9krkeab7dpm41l2i5o3s4
    height = 6
    width = 6
    block = 9
    problem = [
        [0, 0, 1, 1, 1, 2],
        [0, 1, 1, 2, 2, 2],
        [0, 5, 7, 7, 2, 3],
        [6, 5, 5, 3, 3, 3],
        [6, 6, 8, 3, 4, 4],
        [6, 6, 8, 8, 4, 4],
        [1, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 0, 5],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 3, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 4],
    ]
    has_answer, answer = solve_ripple(height, width, block, problem)

    if not has_answer:
        print('no answer', file=sys.stderr)
        return

    for y in range(height):
        for x in range(width):
            if answer[y, x].sol is None:
                print('.', end=' ')
            else:
                print(answer[y, x].sol, end=' ')
        print('')


if __name__ == '__main__':
    _main()
