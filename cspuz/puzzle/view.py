import random
import math
import sys

from cspuz import Solver, graph
from cspuz.puzzle import util


def solve_view(height, width, problem, is_non_con=False, is_anti_knight=False):
    solver = Solver()
    has_number = solver.bool_array((height, width))
    graph.active_vertices_connected(solver, has_number)
    nums = solver.int_array((height, width), 0, height + width)
    solver.add_answer_key(nums)
    solver.add_answer_key(has_number)

    to_up = solver.int_array((height, width), 0, height - 1)
    solver.ensure(to_up[0, :] == 0)
    solver.ensure(to_up[1:, :] == has_number[:-1, :].cond(0, to_up[:-1, :] + 1))

    to_down = solver.int_array((height, width), 0, height - 1)
    solver.ensure(to_down[-1, :] == 0)
    solver.ensure(to_down[:-1, :] == has_number[1:, :].cond(0, to_down[1:, :] + 1))

    to_left = solver.int_array((height, width), 0, width - 1)
    solver.ensure(to_left[:, 0] == 0)
    solver.ensure(to_left[:, 1:] == has_number[:, :-1].cond(0, to_left[:, :-1] + 1))

    to_right = solver.int_array((height, width), 0, width - 1)
    solver.ensure(to_right[:, -1] == 0)
    solver.ensure(to_right[:, :-1] == has_number[:, 1:].cond(0, to_right[:, 1:] + 1))

    solver.ensure(has_number.then(nums == to_up + to_left + to_down + to_right))
    solver.ensure((has_number[:-1, :] & has_number[1:, :]).then(nums[:-1, :] != nums[1:, :]))
    solver.ensure((has_number[:, :-1] & has_number[:, 1:]).then(nums[:, :-1] != nums[:, 1:]))
    solver.ensure((~has_number).then(nums == 0))
    for y in range(height):
        for x in range(width):
            if problem[y][x] >= 0:
                solver.ensure(nums[y, x] == problem[y][x])
                solver.ensure(has_number[y, x])

    if is_non_con:
        graph.numbers_non_consecutive(solver, nums, has_number)

    if is_anti_knight:
        graph.numbers_anti_knight(solver, nums, has_number)

    is_sat = solver.solve()

    return is_sat, nums, has_number


def compute_score(nums):
    score = 0
    for v in nums:
        if v.sol is not None:
            score += 1
    return score


def generate_view(height, width, verbose=False):
    problem = [[-1 for _ in range(width)] for _ in range(height)]
    score = 0
    temperature = 5.0
    fully_solved_score = height * width

    for step in range(height * width * 10):
        cand = []
        for y in range(height):
            for x in range(width):
                for n in range(-1, max(height, width) + 2):
                    if problem[y][x] != n:
                        cand.append((y, x, n))
        random.shuffle(cand)

        for y, x, n in cand:
            n_prev = problem[y][x]
            problem[y][x] = n

            sat, nums, has_number = solve_view(height, width, problem)
            if not sat:
                score_next = -1
                update = False
            else:
                raw_score = compute_score(nums)
                if raw_score == fully_solved_score:
                    return problem, nums, has_number
                clue_score = 0
                for y2 in range(height):
                    for x2 in range(width):
                        if problem[y2][x2] >= 0:
                            clue_score += 3
                score_next = raw_score - clue_score
                update = (score < score_next or random.random() < math.exp((score_next - score) / temperature))

            if update:
                if verbose:
                    print('update: {} -> {}'.format(score, score_next), file=sys.stderr)
                score = score_next
                break
            else:
                problem[y][x] = n_prev

        temperature *= 0.995
    if verbose:
        print('failed', file=sys.stderr)
    return None, None


def _main():
    height = 8
    width = 8
    problem, number, has_number = generate_view(height, width, True)
    if problem is not None:
        for row in problem:
            for num in row:
                if num < 0:
                    print('.', end=' ')
                else:
                    print(num, end=' ')
            print('')
        for y in range(height):
            for x in range(width):
                if has_number[y, x].sol:
                    print(number[y, x].sol, end='')
                else:
                    print(' ', end='')
            print('')
        return

    # https://twitter.com/semiexp/status/1210955179270393856
    is_sat, nums, has_number = solve_view(8, 8, [
        [-1,  4, -1, -1,  2, -1, -1, -1],
        [-1, -1,  2, -1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1,  2],
        [-1, -1, -1, -1,  2, -1, -1, -1],
        [-1, -1, -1, -1, -1,  2, -1, -1],
        [-1, -1,  1, -1, -1,  0, -1, -1],
        [-1,  2, -1, -1, -1, -1, -1, -1],
        [-1, -1, -1,  9, -1, -1, -1,  2],
    ])
    print('has_answer:', is_sat)
    if is_sat:
        ans = []
        for y in range(8):
            row = []
            for x in range(8):
                if has_number[y, x].sol is not None:
                    if has_number[y, x].sol:
                        if nums[y, x].sol is not None:
                            row.append(str(nums[y, x].sol))
                        else:
                            row.append('#')
                    else:
                        row.append('.')
                else:
                    row.append('?')
            ans.append(row)
        print(util.stringify_array(ans))


if __name__ == '__main__':
    _main()
