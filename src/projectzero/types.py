"""Types for PZERO Chess Engine"""

from .exceptions import InvalidFENError

_PIECES: set = {"pawn", "knight", "bishop", "rook", "queen", "king"}

_COSTS: dict[str, int] = {
    "pawn": 100,
    "knight": 300,
    "bishop": 300,
    "rook": 500,
    "queen": 900,
    "king": 1000000,
}

_DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def validate_fen(fen: str) -> None:
    board, active, castling, en_passant, half, full = fen.strip().split(" ")
    if not all([board, active, castling, en_passant, half, full]):
        raise InvalidFENError("FEN string must contain 6 parts")


class Piece:
    def __init__(self, name: str) -> None:
        if name not in _PIECES:
            raise ValueError("invalid piece name!")

        self._name = name
        # no ".get(...)" here since we want the error if something unforeseen happens
        self._cost = _COSTS[name]


class Board:
    def __init__(
        self,
        board: list[list[Piece | None]],
        active_color: str,
        half_moves: int,
        full_moves: int,
    ) -> None:

        _board: list[list[Piece | None]]

        if board:
            self._board = board
        else:
            self._board = [[None for _ in range(8)] for _ in range(8)]

        self._half_moves = half_moves
        self._full_moves = full_moves
        self._move_log: list[str] = []

    def fill_board(self): ...

    def check_legality(self): ...

    # algebraic notation??
    def move(self): ...

    # get piece at pos
    def peek(self, row, col) -> Piece: ...  # row and col or?

    @classmethod
    def from_fen(cls, fen: str) -> Board:
        validate_fen(fen)
        board: list[list[None | Piece]] = [[None for _ in range(8)] for _ in range(8)]

        return cls(
            board,
            " ",
            0,
            0,
        )

    def write_txt_log(self) -> None: ...


__all__ = ["Board", "Piece", "validate_fen"]
