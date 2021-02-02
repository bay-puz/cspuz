import sys
import random

from cspuz import Solver
from cspuz.constraints import count_true
from cspuz.generator import generate_problem, Choice


def solve_darts(target, darts, board):
    solver = Solver()
    is_dart = solver.bool_array(len(board))
    solver.add_answer_key(is_dart)

    solver.ensure(count_true(is_dart) == darts)

    def _sum(d, b):
        sums = 0
        for i in range(len(board)):
            sums += d[i].cond(b[i], 0)
        return sums

    solver.ensure(_sum(is_dart, board) == target)

    is_sat = solver.solve()
    return is_sat, is_dart


def generate_darts(darts=3, size=6, score_range=range(10, 50), target=None, verbose=True):
    pattern = [Choice(list(score_range), None) for _ in range(size)]

    def _target(target, darts, board):
        if target is not None:
            return target
        return sum(board[0:darts])

    def pretest(board):
        for i in range(len(board)):
            for j in range(i+1, len(board)):
                if board[i] == board[j]:
                    return False
        return True

    board = generate_problem(lambda board: solve_darts(_target(target, darts, board), darts, board),
                             builder_pattern=pattern, pretest=pretest, verbose=verbose)

    if board is None:
        return None, None, None
    if target is None:
        target = sum(board[0:darts])
        random.shuffle(board)

    return target, darts, board


def _main():
    if len(sys.argv) == 1:
        target = 126
        darts = 3
        board = [48, 37, 31, 32, 45, 30, 49]

    else:
        darts, size, min, max, target = map(int, sys.argv[1:])
        if target == 0:
            target = None
        target, darts, board = generate_darts(darts, size, range(min, max), target)
        if board is None:
            print('failed to genarate')
            return

    is_sat, ans = solve_darts(target=target, darts=darts, board=board)
    if not is_sat:
        print('no answer')
        return

    print('Target={}'.format(target))
    for _ in range(darts):
        print('🎯', end='')
    print('')
    for i in range(len(board)):
        d = ''
        if ans[i].sol is None:
            d = '?'
        elif ans[i].sol:
            d = '🎯'
        print('{} {}'.format(board[i], d))


if __name__ == '__main__':
    _main()
