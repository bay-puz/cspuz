import sys
import subprocess
from math import sqrt

from cspuz import Solver, graph
from cspuz.constraints import alldifferent
from cspuz.puzzle import util, url
from cspuz.generator import generate_problem, count_non_default_values, ArrayBuilder2D


def solve_sudoku(problem, n=3, is_non_con=False, is_anti_knight=False, is_non_dicon=False, is_anti_alfil=False):
    size = n * n
    solver = Solver()
    answer = solver.int_array((size, size), 1, size)
    solver.add_answer_key(answer)
    for i in range(size):
        solver.ensure(alldifferent(answer[i, :]))
        solver.ensure(alldifferent(answer[:, i]))
    for y in range(n):
        for x in range(n):
            solver.ensure(alldifferent(answer[y*n:(y+1)*n, x*n:(x+1)*n]))
    for y in range(size):
        for x in range(size):
            if problem[y][x] >= 1:
                solver.ensure(answer[y, x] == problem[y][x])

    if is_non_con:
        graph.numbers_non_consecutive(solver, answer)

    if is_anti_knight:
        graph.numbers_anti_knight(solver, answer)

    if is_non_dicon:
        graph.numbers_non_diagonally_consecutive(solver, answer)

    if is_anti_alfil:
        graph.numbers_anti_alfil(solver, answer)

    is_sat = solver.solve()

    return is_sat, answer


def generate_sudoku(n, max_clue=None, symmetry=False, verbose=False):
    size = n * n

    def pretest(problem):
        if max_clue is None:
            return True
        else:
            return count_non_default_values(problem, default=0, weight=1) <= max_clue

    generated = generate_problem(lambda problem: solve_sudoku(problem, n=n),
                                 builder_pattern=ArrayBuilder2D(size, size, range(0, size + 1), default=0, symmetry=symmetry),
                                 pretest=pretest,
                                 clue_penalty=lambda problem: count_non_default_values(problem, default=0, weight=5),
                                 verbose=verbose)
    return generated


def parse_puzz_link_sudoku(puzz_link_url):
    height, width, body = url.split_puzz_link_url(puzz_link_url)
    return int(sqrt(height)), url.decode_numbers(height, width, body, 16)


def to_puzz_link_sudoku(size, problem, variant=False):
    puzz_link_base = 'https://puzz.link/p?sudoku'
    if variant:
        puzz_link_base += '/v:'
    return '{}/{}/{}/{}'.format(puzz_link_base, size*size, size*size, url.encode_numbers(size*size, size*size, problem, max_number=16))


def _main():
    if len(sys.argv) == 1:
        # https://commons.wikimedia.org/wiki/File:Sudoku-by-L2G-20050714.svg
        problem = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]
        is_sat, answer = solve_sudoku(problem)
        if is_sat:
            print(util.stringify_array(answer, dict([(None, '?')] + [(i, str(i)) for i in range(1, 10)])))
    elif len(sys.argv[1]) > 3:
        size, problem = parse_puzz_link_sudoku(sys.argv[1])
        is_sat, answer = solve_sudoku(problem, size)
        if is_sat:
            print(util.stringify_array(answer, dict([(None, '?')] + [(i, str(i)) for i in range(1, 10)])))
        else:
            print('no answer')
    else:
        n = int(sys.argv[1])
        if len(sys.argv) >= 3:
            max_clue = int(sys.argv[2])
        else:
            max_clue = None
        while True:
            try:
                problem = generate_sudoku(n, max_clue=max_clue, symmetry=False, verbose=True)
                if problem is not None:
                    print(to_puzz_link_sudoku(n, problem))
            except subprocess.TimeoutExpired:
                print('timeout', file=sys.stderr)


if __name__ == '__main__':
    _main()
