"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):

    if board == initial_state():  # If board is empty, then X's turn
        return X
    x_count = sum(row.count(X) for row in board)  # Count number of X's on board
    o_count = sum(row.count(O) for row in board)  # Count number of O's on board
    if x_count > o_count:  # If X has played more turns, then O's turn
        return O
    else:  # If O has played equal or more turns, then X's turn
        return X


def actions(board):
    possible_actions = set()
    for i in range(3):  # Rows
        for j in range(3):  # Columns
            if board[i][j] == EMPTY:  # If cell is empty, add to possible actions
                possible_actions.add((i, j))
    return possible_actions  # Return set of possible actions (i, j) where i is row and j is column


def result(board, action):

    i, j = action

    # Check action is within board boundaries
    if i not in range(3) or j not in range(3):
        raise Exception("Invalid action")  # Raise exception

    if board[i][j] is not EMPTY:  # If action is invalid (cell not empty)
        raise Exception("Invalid action")  # Raise exception

    new_board = [row[:] for row in board]
    new_board[i][j] = player(board)  # Place the player's mark on the board
    return new_board  # Return the new board state


def winner(board):
    for i in range(3):  # Check rows and columns for a winner
        if board[i][0] == board[i][1] == board[i][2] != EMPTY:  # Check if row i has all same marks
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != EMPTY:  # Check if column i has all same marks
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] != EMPTY:  # Check diagonal from top-left to bottom-right
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != EMPTY:  # Check diagonal from top-right to bottom-left
        return board[0][2]
    # Above checks all winning conditions and returns either X or O, if none met,
    return None  # Return None if there is no winner


def terminal(board):
    if winner(board) is not None:  # If there is a winner return True, game is over
        return True
    for row in board:  # Check for any empty cells
        if EMPTY in row:
            return False  # If there is at least one empty cell, game is not over
    return True  # If no empty cells and no winner, game is over (draw)


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def min_value(board):
    if terminal(board):
        return utility(board)
    v = 2
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v


def max_value(board):
    if terminal(board):
        return utility(board)
    v = -2
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):  # If game is over, return None
        return None

    current_player = player(board)  # Determine current player

    if current_player == X:  # If current player is X, maximize value
        best_value = -2  # Initialize best value to negative 2 (since utility values are -1, 0, 1)
        best_action = None  # Initialize best action to None
        for action in actions(board):  # Iterate through possible actions
            # Get the minimum value of the resulting board state
            value = min_value(result(board, action))
            if value > best_value:  # If value is greater than best value
                best_value = value  # Update best value
                best_action = action  # Update best action
        return best_action  # Return the best action found
    else:
        best_value = 2  # Initialize best value to 2 (since utility values are -1, 0, 1)
        best_action = None  # Initialize best action to None
        for action in actions(board):  # Iterate through possible actions
            # Get the maximum value of the resulting board state
            value = max_value(result(board, action))
            if value < best_value:  # If value is less than best value
                best_value = value  # Update best value
                best_action = action  # Update best action
        return best_action  # Return the best action found
