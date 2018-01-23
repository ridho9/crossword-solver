import sys


class Struct:
    pass


def put_words(state, current=[]):
    state = [x[:] for x in state]

    for line in current:
        if line[2] == '|':
            for r in range(line[1], line[1] + line[3]):
                state[r][line[0]] = line[4][r - line[1]]
        else:
            state[line[1]][line[0]:line[0] + line[3]] = list(line[4])

    return state


def put_word(state, line):
    state = [x[:] for x in state]

    if line[2] == '|':
        for r in range(line[1], line[1] + line[3]):
            state[r][line[0]] = line[4][r - line[1]]
    else:
        state[line[1]][line[0]:line[0] + line[3]] = list(line[4])

    return state


def print_state(state, current=[]):
    for l in put_words(state, current):
        print(''.join(l))


def load_board_from_file(filename):
    board = Struct()

    with open(filename) as f:
        board.n = int(f.readline().strip())
        test = []

        for i in range(board.n + 2):
            line = []
            for j in range(board.n + 2):
                line.append('#')
            test.append(line)
        for l in test[1:-1]:
            l[1:-1] = list(f.readline().strip())

        board.layout = test
        board.words = [x for x in f.readline().strip().split(';') if x != '']
        board.state = list(board.layout)

    return board


def detect_slot(state, orientation):
    if orientation == '|':
        # transpose board
        state = list(zip(*state))

    slot = []
    for row in range(len(state)):
        line = ''.join(state[row])

        index = -1
        while True:
            index = line.find('#--', index + 1)
            if index == -1:
                break

            # determine length
            le = len(line[index + 1:].partition('#')[0])

            if orientation == '|':
                coor = (row, index + 1, '|', le)
            else:
                coor = (index + 1, row, '-', le)
            slot.append(coor)

    return slot


def solve(state, slots, words, current=[]):
    if len(slots) == 0:
        return (state, current)

    current_slot = slots[0]
    curlen_words = [x for x in words if len(x) == current_slot[3]]

    fit_state = [x[:] for x in state]

    # for every possible words for our current slot
    for try_word in curlen_words:
        # check if we can insert try_word to current_slot
        # create slice of the range
        test_slot = []
        can_fit = True

        if current_slot[2] == '-':
            test_slot = fit_state[current_slot[1]]
            test_slot = test_slot[current_slot[0]:
                                  current_slot[0]+current_slot[3]]
        else:
            test_slot = list(zip(*fit_state))[current_slot[0]]
            test_slot = test_slot[current_slot[1]:
                                  current_slot[1]+current_slot[3]]

        # check for no collision
        check_range = filter(lambda x: x[0] != '-', zip(test_slot, try_word))
        for item in check_range:
            can_fit = can_fit and (item[0] == item[1])

        if can_fit is not True:
            continue

        line = (*current_slot, try_word)

        left_words = [x for x in words if x != try_word]
        left_slots = slots[1:]
        next_current = current.copy()
        next_current.append(line)

        # put the curent word to fit_state
        test_state = put_word(fit_state, line)

        next_recursion = solve(test_state, left_slots,
                               left_words, next_current)
        if next_recursion != -1:
            return next_recursion
    return -1


def solve_file(filename):
    board = load_board_from_file(filename)
    print_state(board.layout)
    board.words.sort(key=lambda x: -len(x))
    print(board.words)

    slots = detect_slot(board.layout, '-') + detect_slot(board.layout, '|')
    slots.sort(key=lambda x: -x[3])

    try:
        state, current = solve(board.layout, slots, board.words)
        print('SOLUTION FOUND')
        print_state(state, current)
    except Exception as e:
        print('NO SOLUTION')


if __name__ == "__main__":
    from datetime import datetime
    start_time = datetime.now()

    if len(sys.argv) != 2:
        print("Usage: python3 {} [filename]".format(sys.argv[0]))
        sys.exit()

    filename = sys.argv[1]
    print("Reading from {}".format(filename))

    solve_file(filename)

    print("Elapsed time : {}".format(datetime.now() - start_time))
