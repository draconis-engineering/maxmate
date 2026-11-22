"""Types for the Visio Chess Engine"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import datetime
from pathlib import Path

from ._types import _BoardType, _Square
from .exceptions import InvalidSANError
from .piece import ChessPiece
from .san_fen import _DEFAULT_FEN, build_board_from_fen, parse_fen, validate_san

# ====================================
# Helpers /  /  /  /  /  /  /  /  /  /
# ====================================


def _require_int(o: Sequence[object], func: Callable) -> None:
    for i in o:
        if not isinstance(i, int) or isinstance(i, bool):
            raise TypeError(f"function {func.__name__} requires integers")


class ChessBoard:
    def __init__(
        self,
        board: _BoardType | None = None,
        /,
        active_color: str = "w",
        castling: str = "KQkq",
        en_passant: str = "-",
        half_moves: int = 0,
        full_moves: int = 1,
    ) -> None:

        # --- Board State & Helpers ---
        self._board: _BoardType = (
            board if board is not None else build_board_from_fen(_DEFAULT_FEN)
        )
        self._active_color = active_color
        self._castling = castling
        self._en_passant = en_passant
        self._half_moves = half_moves
        self._full_moves = full_moves

        # --- Engine Helpers ---
        self._move_log: list[str] = []
        self._taken_pieces: list[ChessPiece] = []

    def __getitem__(self, idx: int, /) -> list[_Square]:
        _require_int([idx], ChessBoard.__getitem__)
        return self._board[idx]

    def check_legality(self): ...

    def move(self, notation: str, /) -> bool:
        return True

    # --- get piece at pos ---
    def peek_algebraic(self, notation: str, /) -> _Square: ...

    @classmethod
    def from_fen(cls, fen: str, /) -> ChessBoard:
        return cls(*parse_fen(fen))

    def log_move(self, san: str) -> None:
        if not validate_san(san):
            raise InvalidSANError("invalid SAN string -> logging of move failed")

        self._move_log.append(san)

    def save_log(self, path: Path):
        with open(str(path / f"log_{datetime.now()}.txt"), "x") as f:
            ...


__all__ = ["ChessBoard"]
