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
    state = put_words(state, current)
    height = len(state)
    width = len(state[0])

    # start drawing
    # first row
    for col in range(width):
        if col == 0:
            print('┌', end='')
        else:
            print('┬', end='')
        print('─', end='')
    print('┐')

    for row in range(height):
        for col in range(width):
            if state[row][col] == '#':
                print('│ ', end='')
            else:
                print('│\033[1;37m{}\033[0m'
                      .format(state[row][col].upper()), end='')
        print('│')
        if row == height - 1:
            break
        for col in range(width):
            if col == 0:
                print('├', end='')
            else:
                print('┼', end='')
            print('─', end='')
        print('┤')

    # last line
    for col in range(width):
        if col == 0:
            print('└', end='')
        else:
            print('┴', end='')
        print('─', end='')
    print('┘')


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
        can_fit = True

        # check for no collision
        if current_slot[2] == '-':
            for col in range(current_slot[0], current_slot[0] + len(try_word)):
                if fit_state[current_slot[1]][col] != '-':
                    can_fit &= try_word[col - current_slot[0]] \
                               == fit_state[current_slot[1]][col]
                if can_fit is not True:
                    break
        else:
            for row in range(current_slot[1], current_slot[1] + len(try_word)):
                if fit_state[row][current_slot[0]] != '-':
                    can_fit &= try_word[row - current_slot[1]] \
                               == fit_state[row][current_slot[0]]
                if can_fit is not True:
                    break

        if can_fit is not True:
            continue

        line = (*current_slot, try_word)

        # left_words = [x for x in words if x != try_word]
        left_words = words.copy()
        left_words.remove(try_word)
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
    # print_state(board.layout)
    board.words.sort(key=lambda x: -len(x))
    # print(board.words)

    slots = detect_slot(board.layout, '-') + detect_slot(board.layout, '|')
    slots.sort(key=lambda x: -x[3])

    try:
        state, current = solve(board.layout, slots, board.words)
        print('SOLUTION FOUND')
        print_state(state, current)
    except Exception as e:
        print('NO SOLUTION')
        assert False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 {} [filename]".format(sys.argv[0]))
        sys.exit()

    from datetime import datetime
    start_time = datetime.now()

    filename = sys.argv[1]
    print("Reading from {}".format(filename))

    solve_file(filename)

    print("Elapsed time : {}".format(datetime.now() - start_time))
