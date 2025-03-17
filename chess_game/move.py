# ## Load current fen
# ## Make a move
# ## Evaluate if lost
# ## If not make a move
# ## Evaluate if won
# ## If not save FEN
# from stockfish import Stockfish

# def move(chess_move: str):

#!/usr/bin/env python
import logging
import os
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


def get_stockfish_engine() -> Stockfish:
    root_path = getenv_or_raise_runtime("ROOT_PATH")
    return Stockfish(f"{root_path}/stockfish/stockfish")


def make_a_move_or_raise_exception(
    stockfish: Stockfish, suggested_move: str | None = None
) -> str:
    inital_fen_position = stockfish.get_fen_position()
    best_move_by_stockfish = stockfish.get_best_move()
    if best_move_by_stockfish is None:
        stockfish_evaluation = stockfish.get_evaluation()
        if stockfish_evaluation and stockfish_evaluation.get("type") == "mate":
            return "mate"
        else:
            return "stalemate"

    move = suggested_move if suggested_move is not None else best_move_by_stockfish
    stockfish.make_moves_from_current_position([move])

    new_fen_position = stockfish.get_fen_position()

    if inital_fen_position == new_fen_position:
        return "illegal"

    return move


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Apply a chess move using the Stockfish Python wrapper (without python-chess)."
    )
    parser.add_argument(
        "move", type=str, help="Chess move in UCI notation (e.g., e2e4)"
    )
    args = parser.parse_args()

    # Init stockfish and set current chess board.
    stockfish = get_stockfish_engine()
    fen_position = get_current_fen_position()
    stockfish.set_fen_position(fen_position)

    # Apply the move provided by the user
    move = make_a_move_or_raise_exception(
        stockfish=stockfish, suggested_move=args.move
    )

    if move == "mate":
        print("Winner: Engine")
        return

    if move == "stalemate":
        print("Stalemate")
        return

    if move == "illegal":
        print(f"Move {move} is not allowed.")
        return

    print("Model's move:")
    print(stockfish.get_board_visual())
    print()

    # Make stockfish engine make a move
    # Apply the move provided by the user
    move = make_a_move_or_raise_exception(stockfish=stockfish)

    if move == "mate":
        print("Winner: Agent")
        return

    if move == "stalemate":
        print("Stalemate")
        return

    if move == "illegal":
        print(f"Move {move} by stockfish is not allowed.")
        return

    print("Stockfish's move:")
    print(stockfish.get_board_visual())
    print()


if __name__ == "__main__":
    main()
