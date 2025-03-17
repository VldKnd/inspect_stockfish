## Experiment setup:
```
.root/
    chess_positions_as_fen.txt
    stockfish_engine
    game.py
    ...
```
Model can call game.py with move in FEN notation
## Requiered installations:

Installing uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Installing brew:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Installing the stockfish engine:
```bash
brew install stockfish
```

Setting the env variables ( Have to be run from the root of the package ):
```bash
set -a && source .env && set +a
```
