import sys

from cspuz import Solver, alldifferent


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


def _main():
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


if __name__ == '__main__':
    _main()
