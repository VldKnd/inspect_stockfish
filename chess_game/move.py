#!/usr/bin/env python
import textwrap
import logging
import os
import typing
import argparse
from stockfish import Stockfish

LOGGER = logging.getLogger(__name__)


def getenv_or_raise_runtime(key: str) -> str:
    environment_variable = os.getenv(key, None)

    if environment_variable is None:
        raise RuntimeError(f"Environment variable {key} is not set.")

    LOGGER.debug(f"Looking up environment variable {key}={environment_variable}")
    return environment_variable


def get_current_fen_position() -> str:
    root_path = getenv_or_raise_runtime("ROOT_PATH")
    with open(f"{root_path}/chess_game/chess_positions_as_fen.txt", "r") as file:
        return file.read()


def update_current_fen_position(fen_position: str) -> int:
    root_path = getenv_or_raise_runtime("ROOT_PATH")
    with open(f"{root_path}/chess_game/chess_positions_as_fen.txt", "w") as file:
        return file.write(fen_position)


def get_stockfish_engine() -> Stockfish:
    root_path = getenv_or_raise_runtime("ROOT_PATH")
    return Stockfish(f"{root_path}/stockfish/stockfish")


def get_active_color(fen: str) -> str:
    """
    Extracts the active color from a FEN string.

    Parameters:
        fen (str): A valid FEN string.

    Returns:
        str: 'w' if it's White's turn, 'b' if it's Black's turn.

    Raises:
        ValueError: If the FEN string is invalid or doesn't contain an active color.
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
    inital_fen_position = stockfish.get_fen_position()

    try:
        stockfish.make_moves_from_current_position([move])
    except ValueError:
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
                -- Stockfish move following user's move in UCI notation. e.g. e7e5\n
        """)
    )
    parser.add_argument(
        "move", type=str, help="Chess move in UCI notation (e.g., e2e4)"
    )
    args = parser.parse_args()

    # Init stockfish and set current chess board.
    stockfish = get_stockfish_engine()
    fen_position = get_current_fen_position()
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
