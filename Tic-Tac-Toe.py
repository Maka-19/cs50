"""
Tic Tac Toe Player
"""

import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """Returns starting state of the board."""
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """Returns player who has the next turn on a board."""
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)
    return X if x_count <= o_count else O


def actions(board):
    """Returns set of all possible actions (i, j) available on the board."""
    possible = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible.add((i, j))
    return possible


def result(board, action):
    """Returns the board that results from making move (i, j) on the board."""
    i, j = action
    if i < 0 or i > 2 or j < 0 or j > 2:
        raise ValueError("Action out of bounds")
    if board[i][j] != EMPTY:
        raise ValueError("Cell already occupied")
    
    new_board = copy.deepcopy(board)
    new_board[i][j] = player(board)
    return new_board


def winner(board):
    """Returns the winner of the game, if there is one."""
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] and row[0] is not None:
            return row[0]
    
    # Check columns
    for j in range(3):
        if board[0][j] == board[1][j] == board[2][j] and board[0][j] is not None:
            return board[0][j]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2]
    
    return None


def terminal(board):
    """Returns True if game is over, False otherwise."""
    if winner(board) is not None:
        return True
    # Check if any empty cells remain
    for row in board:
        if EMPTY in row:
            return False
    return True


def utility(board):
    """Returns 1 if X has won, -1 if O has won, 0 otherwise."""
    w = winner(board)
    if w == X:
        return 1
    elif w == O:
        return -1
    return 0


def minimax(board):
    """Returns the optimal action for the current player on the board."""
    if terminal(board):
        return None
    
    current = player(board)
    
    if current == X:
        _, move = max_value(board)
    else:
        _, move = min_value(board)
    
    return move


def max_value(board):
    """Returns (utility, best_action) for maximizing player."""
    if terminal(board):
        return utility(board), None
    
    v = float('-inf')
    best = None
    for action in actions(board):
        min_val, _ = min_value(result(board, action))
        if min_val > v:
            v = min_val
            best = action
        if v == 1:  # Alpha-beta pruning optimization
            break
    return v, best


def min_value(board):
    """Returns (utility, best_action) for minimizing player."""
    if terminal(board):
        return utility(board), None
    
    v = float('inf')
    best = None
    for action in actions(board):
        max_val, _ = max_value(result(board, action))
        if max_val < v:
            v = max_val
            best = action
        if v == -1:  # Alpha-beta pruning optimization
            break
    return v, best