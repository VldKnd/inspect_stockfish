#!/usr/bin/env python
import textwrap
import os
import typing
import argparse
from stockfish import Stockfish


def getenv_or_raise_runtime(key: str) -> str:
    """
    Retrieves the value of an environment variable or raises an error if it is not set.

    This function attempts to fetch the value of the specified environment variable.
    If the variable is not found, a `RuntimeError` is raised. Otherwise, the value
    is returned and logged for debugging purposes.

    Parameters
    ----------
    key : str
        The name of the environment variable to retrieve.

    Returns
    -------
    str
        The value of the requested environment variable.

    Raises
    ------
    RuntimeError
        If the specified environment variable is not set.
    """
    environment_variable = os.getenv(key, None)

    if environment_variable is None:
        raise RuntimeError(f"Environment variable {key} is not set.")

    return environment_variable


def get_current_fen_position() -> str:
    """
    Retrieves the current chess board position in FEN notation.

    This function reads the latest chess position from a file located at
    `chess_positions_as_fen.txt` within the chess game directory. The root path
    of the project is obtained from the `ROOT_PATH` environment variable.

    Returns
    -------
    str
        The current chess board position in FEN notation.

    Raises
    ------
    RuntimeError
        If the `ROOT_PATH` environment variable is not set.
    FileNotFoundError
        If the `chess_positions_as_fen.txt` file does not exist.
    IOError
        If there is an error reading the file.
    """
    root_path = getenv_or_raise_runtime("ROOT_PATH")
    with open(f"{root_path}/chess_game/chess_positions_as_fen.txt", "r") as file:
        return file.read()


def update_current_fen_position(fen_position: str) -> int:
    """
    Updates the current chess board position in FEN notation.

    This function writes the given FEN position to the `chess_positions_as_fen.txt` file
    within the chess game directory. The root path of the project is obtained from the
    `ROOT_PATH` environment variable.

    Parameters
    ----------
    fen_position : str
        The FEN notation string representing the current state of the chess board.

    Returns
    -------
    int
        The number of characters written to the file.

    Raises
    ------
    RuntimeError
        If the `ROOT_PATH` environment variable is not set.
    IOError
        If there is an error writing to the file.
    """
    root_path = getenv_or_raise_runtime("ROOT_PATH")
    with open(f"{root_path}/chess_game/chess_positions_as_fen.txt", "w") as file:
        return file.write(fen_position)


def get_stockfish_engine() -> Stockfish:
    """
    Initializes and returns an instance of the Stockfish chess engine.

    This function retrieves the root path from the `ROOT_PATH` environment variable
    and initializes a Stockfish engine instance using the executable located in the
    `stockfish` directory.

    Returns
    -------
    Stockfish
        An instance of the Stockfish chess engine.

    Raises
    ------
    RuntimeError
        If the `ROOT_PATH` environment variable is not set.
    FileNotFoundError
        If the Stockfish executable is not found at the expected path.
    """
    root_path = getenv_or_raise_runtime("ROOT_PATH")
    return Stockfish(f"{root_path}/stockfish/stockfish")


def get_active_color(fen: str) -> str:
    """
    Extracts the active color from a FEN (Forsyth-Edwards Notation) string.

    The function parses the FEN string and returns the character representing
    the player to move: `'w'` for White and `'b'` for Black.

    Parameters
    ----------
    fen : str
        A valid FEN string representing the current chess position.

    Returns
    -------
    str
        `'w'` if it is White's turn, `'b'` if it is Black's turn.

    Raises
    ------
    ValueError
        If the FEN string is invalid or does not contain a valid active color.
    """
    tokens = fen.strip().split()
    if len(tokens) < 2:
        raise ValueError("Invalid FEN string: not enough fields.")
    active_color = tokens[1]
    if active_color not in ("w", "b"):
        raise ValueError("Invalid active color in FEN: must be 'w' or 'b'.")
    return active_color


def move_and_evaluate(
    stockfish: Stockfish, move: str
) -> typing.Literal["illegal", "white", "black", "stale", "move"]:
    """
    Executes a move in Stockfish and evaluates the game state.

    This function attempts to make a move in the given Stockfish instance. It determines
    if the move is illegal, results in checkmate for either player, leads to a stalemate,
    or is a valid move that continues the game.

    Parameters
    ----------
    stockfish : Stockfish
        An instance of the Stockfish chess engine.
    move : str
        A chess move in UCI (Universal Chess Interface) notation.

    Returns
    -------
    Literal["illegal", "white", "black", "stale", "move"]
        - `"illegal"` if the move is not valid.
        - `"white"` if White wins by checkmate.
        - `"black"` if Black wins by checkmate.
        - `"stale"` if the game ends in a stalemate.
        - `"move"` if the game continues normally.

    Raises
    ------
    Exception
        If there is an unexpected error when making the move.
    """
    inital_fen_position = stockfish.get_fen_position()

    try:
        stockfish.make_moves_from_current_position([move])
    except Exception:
        return "illegal"

    new_fen_position = stockfish.get_fen_position()

    if inital_fen_position == new_fen_position:
        return "illegal"

    if stockfish.get_best_move() is None:
        stockfish_evaluation = stockfish.get_evaluation()

        if stockfish_evaluation and stockfish_evaluation.get("type") == "mate":
            active_color = get_active_color(new_fen_position)
            if active_color == "b":
                return "white"
            else:
                return "black"
        else:
            return "stale"

    return "move"


def print_decision(decision: typing.Literal["white", "black", "stale", "illegal"]):
    """
    Prints the outcome of a chess game based on the provided decision.

    This function takes the result of a game (winner or draw) and prints a corresponding message
    indicating the outcome of the game: either the winning player, stalemate, or an illegal move.

    Parameters
    ----------
    decision : Literal["white", "black", "stale", "illegal"]
        A string indicating the game outcome:
        - `"white"`: White wins.
        - `"black"`: Black wins.
        - `"stale"`: The game ends in a stalemate.
        - `"illegal"`: The move is illegal.

    Returns
    -------
    None
        This function does not return any value, it only prints the result.
    """
    if decision == "white" or decision == "black":
        print(f"winner: {decision}")
    elif decision == "stale":
        print("stalemate")
    else:
        print("illegal move")


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description=textwrap.dedent("""
            Apply a chess move playing as white using the Stockfish Python wrapper.
            Current game state is saved in chess_positions_as_fen.txt file.
            After each move one of the following is returned:\n
                -- winner: white\n
                -- winner: black\n
                -- stalemate\n
                -- illegal move\n
                -- black move: Stockfish move following user's move in UCI notation. e.g. black move: e7e5\n
        """)
    )
    parser.add_argument(
        "move", type=str, help="Chess move in UCI notation (e.g., e2e4)"
    )
    args = parser.parse_args()

    # Init stockfish and set current chess board.
    stockfish = get_stockfish_engine()
    fen_position = get_current_fen_position()
    if get_active_color(fen_position) == "b":
        print("White shoud be making a move first. Aborting.")
        return

    stockfish.set_fen_position(fen_position)

    users_move = args.move
    evaluation_decision = move_and_evaluate(stockfish=stockfish, move=users_move)
    if evaluation_decision != "move":
        print_decision(decision=evaluation_decision)
        return

    stockfish_move = stockfish.get_best_move()
    evaluation_decision = move_and_evaluate(stockfish=stockfish, move=stockfish_move)

    if evaluation_decision != "move":
        print_decision(decision=evaluation_decision)
        return

    print(f"black move: {stockfish_move}")
    update_current_fen_position(stockfish.get_fen_position())


if __name__ == "__main__":
    main()
