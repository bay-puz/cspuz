import math
import random
import sys

from cspuz import Solver, graph
from cspuz.constraints import count_true
from cspuz.puzzle import util, url


def solve_sukoro(height, width, problem, is_anti_knight=False):
    solver = Solver()

    has_number = solver.bool_array((height, width))
    graph.active_vertices_connected(solver, has_number)
    nums = solver.int_array((height, width), -1, 4)
    solver.add_answer_key(nums)
    solver.add_answer_key(has_number)

    for y in range(height):
        for x in range(width):
            neighbors = []
            if y > 0:
                neighbors.append(has_number[y-1, x])
                solver.ensure((has_number[y, x] & has_number[y-1, x]).then(nums[y, x] != nums[y-1, x]))
            if y < height - 1:
                neighbors.append(has_number[y+1, x])
                solver.ensure((has_number[y, x] & has_number[y+1, x]).then(nums[y, x] != nums[y+1, x]))
            if x > 0:
                neighbors.append(has_number[y, x-1])
                solver.ensure((has_number[y, x] & has_number[y, x-1]).then(nums[y, x] != nums[y, x-1]))
            if x < width - 1:
                neighbors.append(has_number[y, x+1])
                solver.ensure((has_number[y, x] & has_number[y, x+1]).then(nums[y, x] != nums[y, x+1]))
            solver.ensure(has_number[y, x].then(count_true(neighbors) == nums[y, x]))

    solver.ensure((~has_number).then(nums < 0))

    for y in range(height):
        for x in range(width):
            if problem[y][x] >= 0:
                solver.ensure(nums[y, x] == problem[y][x])
                solver.ensure(has_number[y, x])

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


def generate_sukoro(height, width, verbose=False):
    problem = [[-1 for _ in range(width)] for _ in range(height)]
    score = 0
    temperature = 5.0
    fully_solved_score = height * width

    for step in range(height * width * 10):
        cand = []
        for y in range(height):
            for x in range(width):
                for n in range(1, 5):
                    if problem[y][x] != n:
                        cand.append((y, x, n))
        random.shuffle(cand)

        for y, x, n in cand:
            n_prev = problem[y][x]
            problem[y][x] = n

            sat, nums, has_number = solve_sukoro(height, width, problem)
            if not sat:
                score_next = -1
                update = False
            else:
                raw_score = compute_score(nums)
                if raw_score == fully_solved_score:
                    return problem
                clue_score = 0
                for y2 in range(height):
                    for x2 in range(width):
                        if problem[y2][x2] > 0:
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
    return None


def generate_sukoro_numbers_set(height, width, verbose=False, set=2, limit=10000):
    fully_solved_score = height * width

    for step in range(1, limit+1):
        cand = []
        for y in range(height):
            for x in range(width):
                cand.append((y, x))
        random.shuffle(cand)

        problem = [[-1 for _ in range(width)] for _ in range(height)]
        i = 0
        for y, x in cand:
            if i > set * 4 - 1:
                break
            problem[y][x] = int(i/set) + 1
            i += 1

        sat, nums, has_number = solve_sukoro(height, width, problem)
        if sat:
            if compute_score(nums) == fully_solved_score:
                return problem

        if verbose and step % 100 == 0:
            print("{}/{}".format(step, limit), file=sys.stderr)

    if verbose:
        print('failed', file=sys.stderr)
    return None


def to_puzz_link_sukoro(height, width, problem, variant=False):
    puzz_link_base = 'https://puzz.link/p?sukoro'
    if variant:
        puzz_link_base += '/v:'
    return '{}/{}/{}/{}'.format(puzz_link_base, width, height, url.encode_numbers(height, width, problem, True, 4))


def parse_puzz_link_sukoro(puzz_link_url):
    height, width, body = url.split_puzz_link_url(puzz_link_url)
    return height, width, url.decode_numbers(height, width, body)


def _main():
    if len(sys.argv) < 3:
        puzz_link = 'http://puzz.link/p?sukoro/8/8/j3d1b2a4b33c2b2d3a13h1a2b1d1d1'
        if len(sys.argv) == 2:
            puzz_link = sys.argv[1]
        print('problem: {}'.format(puzz_link))
        height, width, problem = parse_puzz_link_sukoro(puzz_link)
        is_sat, nums, has_number = solve_sukoro(height, width, problem)
        print('has_answer:', is_sat)
        if is_sat:
            ans = []
            for y in range(height):
                row = []
                for x in range(width):
                    if has_number[y, x].sol is not None:
                        if has_number[y, x].sol:
                            if nums[y, x].sol is not None:
                                row.append(str(nums[y, x].sol))
                            else:
                                row.append('o')
                        else:
                            row.append('x')
                    else:
                        row.append('?')
                ans.append(row)
            print(util.stringify_array(ans))
    elif len(sys.argv) == 3:
        height, width = map(int, sys.argv[1:])
        problem = generate_sukoro(height, width, True)
        if problem is not None:
            print(to_puzz_link_sukoro(height, width, problem))
    elif len(sys.argv) == 5:
        height, width, set, limit = map(int, sys.argv[1:])
        problem = generate_sukoro_numbers_set(height, width, True, set, limit)
        if problem is not None:
            print(to_puzz_link_sukoro(height, width, problem))


if __name__ == '__main__':
    _main()
