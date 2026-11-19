"""Types for the P1 Chess Engine"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence

from .exceptions import InvalidFENError

# ===================================
# Universal Helpers / / / / / / / / /
# ===================================


# --- Type helpers ---
def _require_int(o: Sequence[object], func: Callable) -> None:
    for i in o:
        if not isinstance(i, int) or isinstance(i, bool):
            raise TypeError(f"function {func.__name__} requires integers")


# --- Chess-specific helpers ---
def _algebraic_to_xy(notation: str, /) -> tuple[int, int]: ...


def _xy_to_algebraic(x: int, y: str, /) -> str: ...


_PIECES = {"pawn", "knight", "bishop", "rook", "queen", "king"}
_COLORS = {"white", "w", "black", "b"}
_COSTS = {
    "pawn": 100,
    "knight": 300,
    "bishop": 300,
    "rook": 500,
    "queen": 900,
    "king": 1000000,  # High cost to tell the engine its pricelessness
}

# ===================================
# Piece / / / / / / / / / / / / / / /
# ===================================


class Piece:
    def __init__(self, name: str, color: str) -> None:
        if name not in _PIECES:
            raise ValueError("invalid piece name!")

        self._name = name
        self._cost = _COSTS[name]

        if not color.lower() in _COLORS:
            raise ValueError(f"invalid color: {color}")

        self._color = color.lower()


# ===================================
# Board / / / / / / / / / / / / / / /
# ===================================

# --- Type Aliases ---
type _Square = Piece | None
type _BoardType = list[list[_Square]]

# --- * --- FEN Parsing --- * ---

# Board, active color, castling rights, en passant avaliability, half moves, full moves
_DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def validate_fen(fen: str) -> None:
    parts = fen.split()
    if len(parts) != 6:
        raise InvalidFENError(f"a FEN string needs 6 parts, not {len(parts)}")

    placement, turn, castling, ep, halfmove, fullmove = parts

    # Validate piece placement
    ranks = placement.split("/")
    if len(ranks) != 8:
        raise InvalidFENError(f"FEN string ranks needs 8 parts, not {len(ranks)}")

    # Validate board
    valid_pieces = set("prnbqkPRNBQK")
    for rank in ranks:
        square_count = 0
        for char in rank:
            if char.isdigit() and "1" <= char <= "8":
                square_count += int(char)
            elif char in valid_pieces:
                square_count += 1
            else:
                raise InvalidFENError(f"Unknown chess character: {char}")
        if square_count != 8:
            raise InvalidFENError(f"Invalid board dimension: {square_count}")

    # Validate active color
    if turn not in ("w", "b"):
        raise InvalidFENError(f"Invalid chess color: {turn}")

    # Validate castling availability
    if not re.fullmatch(r"-|K?Q?k?q?", castling):
        raise InvalidFENError(f"Invalid castling configuration: {castling}")

    # Validate en passant target square
    if not re.fullmatch(r"-|[a-h][36]", ep):
        raise InvalidFENError(f"Invalid en passant configuration: {ep}")

    # Validate halfmove clock and fullmove number
    if not halfmove.isdigit() and fullmove.isdigit() and int(fullmove) >= 1:
        raise InvalidFENError(
            f"Invalid halfmove/fullmove counts: {halfmove}, {fullmove}"
        )


def build_board_from_fen(fen: str, /) -> _BoardType: ...


class Board:
    def __init__(
        self,
        board: _BoardType,
        /,
        active_color: str = "w",
        castling: str = "KQkq",
        en_passant: str = "-",
        half_moves: int = 0,
        full_moves: int = 1,
    ) -> None:

        # --- Board State & Helpers ---
        self._board: _BoardType = (
            board if board else [[None for _ in range(8)] for _ in range(8)]
        )
        self._active_color = active_color
        self._castling = castling
        self._en_passant = en_passant
        self._half_moves = half_moves
        self._full_moves = full_moves

        # --- Engine Helpers ---
        self._move_log: list[str] = []
        self._taken_pieces: list[_Square] = []

    def __getitem__(self, idx: int, /) -> list[_Square]:
        _require_int([idx], Board.__getitem__)
        return self._board[idx]

    def check_legality(self, /): ...

    # algebraic notation?? xy for now
    def move(self, /): ...

    # --- get piece at pos, either x-y coords or algebraic not. ---
    def peek_xy(self, row: int, col: int, /) -> _Square:
        if not isinstance(row, int) or isinstance(row, bool):
            raise TypeError("index must be an integer")
        return self._board[row][col]

    def peek_algebraic(self, notation: str, /) -> _Square:
        return self.peek_xy(*_algebraic_to_xy(notation))

    @classmethod
    def from_fen(cls, fen: str, /) -> Board:
        validate_fen(fen)
        board = build_board_from_fen(fen)

        return cls(board)

    def write_txt_log(self, /) -> None: ...


__all__ = ["Board", "Piece", "validate_fen"]
