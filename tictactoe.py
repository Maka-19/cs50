import copy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns the starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    X goes first. After that, players alternate.
    """
    # Count X and O
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)
    return X if x_count == o_count else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    if terminal(board):
        return set()
    acts = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                acts.add((i, j))
    return acts


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    The original board must not be modified.
    If action is invalid, raise an exception.
    """
    i, j = action
    if not (0 <= i < 3 and 0 <= j < 3):
        raise Exception("Invalid action: out of range")
    if board[i][j] != EMPTY:
        raise Exception("Invalid action: cell is not empty")

    new_board = copy.deepcopy(board)
    new_board[i][j] = player(board)
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one (X or O). Otherwise None.
    """
    # Check rows
    for i in range(3):
        if board[i][0] is not None and board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]

    # Check columns
    for j in range(3):
        if board[0][j] is not None and board[0][j] == board[1][j] == board[2][j]:
            return board[0][j]

    # Check diagonals
    if board[0][0] is not None and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] is not None and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]

    return None


def terminal(board):
    """
    Returns True if game is over (win or tie), False otherwise.
    """
    if winner(board) is not None:
        return True
    # If any EMPTY cell exists, not terminal
    for row in board:
        if EMPTY in row:
            return False
    return True


def utility(board):
    """
    Returns the utility of the board:
    1 if X has won, -1 if O has won, 0 otherwise (tie).
    Assumes board is terminal.
    """
    w = winner(board)
    if w == X:
        return 1
    elif w == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    If board is terminal, returns None.
    """

    if terminal(board):
        return None

    current = player(board)

    # Define helpers that return (value, action)
    def max_value(state):
        if terminal(state):
            return utility(state), None
        v = -math.inf
        best_action = None
        for action in actions(state):
            val, _ = min_value(result(state, action))
            if val > v:
                v = val
                best_action = action
                # Early win shortcut
                if v == 1:
                    break
        return v, best_action

    def min_value(state):
        if terminal(state):
            return utility(state), None
        v = math.inf
        best_action = None
        for action in actions(state):
            val, _ = max_value(result(state, action))
            if val < v:
                v = val
                best_action = action
                # Early loss shortcut
                if v == -1:
                    break
        return v, best_action

    if current == X:
        _, action = max_value(board)
    else:
        _, action = min_value(board)

    return action
