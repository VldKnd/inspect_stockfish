FROM ghcr.io/astral-sh/uv:debian

COPY pyproject.toml pyproject.toml
ENV PATH="/.venv/bin:${PATH}"
ENV ROOT_PATH="/"

RUN curl -L https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64.tar --output stockfish.tar
RUN tar xvf stockfish.tar
RUN mv stockfish/stockfish-ubuntu-x86-64 stockfish/stockfish
RUN uv sync

COPY chess_game chess_game
WORKDIR /chess_game