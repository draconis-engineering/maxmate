"""Types for the Visio Chess Engine"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.visio.move import Move

from ._types import _BLACK, _WHITE, _BoardType, _Square
from .exceptions import InvalidSANError
from .piece import ChessPiece
from .san_fen import _DEFAULT_FEN, build_board_from_fen, parse_fen, validate_san
from .utils import (
    _require_int,
    algebraic_to_xy,
    xy_to_algebraic,
)

# ====================================
# Helpers /  /  /  /  /  /  /  /  /  /
# ====================================


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
        """Initializes a ChessBoard"""

        # --- Board State & Helpers ---
        self._board: _BoardType = (
            board if board is not None else build_board_from_fen(_DEFAULT_FEN)
        )
        self._active_color = active_color
        self._castling = castling
        self._en_passant = en_passant
        self._half_moves = half_moves
        self._full_moves = full_moves

        self._is_checked = {_WHITE: False, _BLACK: False}
        self._is_mated = {_WHITE: False, _BLACK: False}

        self._white_attack_map = [[False] * 8 for _ in range(8)]
        self._black_attack_map = [[False] * 8 for _ in range(8)]
        self._last_board = list(self._board)

        # --- Engine Helpers ---
        self._move_log: list[str] = []
        self._taken_pieces: list[ChessPiece] = []

    def __getitem__(self, key: int, /) -> list[_Square]:
        _require_int([key], ChessBoard.__getitem__)
        return self._board[key]

    # Attacked by white, black or both
    def is_square_attacked(self, san: str) -> tuple[bool, bool]:
        if not validate_san(san, is_pos=True):
            raise InvalidSANError()
        _x, _y = algebraic_to_xy(san)
        return True, True

    def update_attack_map(self) -> None:
        for x, rank in enumerate(self._board):
            for y, _ in enumerate(rank):
                self._white_attack_map[x][y], self._black_attack_map[x][y] = (
                    self.is_square_attacked(xy_to_algebraic(x, y))
                )

    def check_legality(self, move: Move) -> bool:
        """Checks if a move is legal based on the current game state"""
        return NotImplemented

    @staticmethod
    def get_legal_moves() -> list[Move]:
        """Returns all the current legal moves that the active color can do"""
        return NotImplemented

    def move(self, move: Move, /) -> bool:
        """Performs a move"""

        if move in self.get_legal_moves():  # This isnt correct though...
            # Parse PosSAN
            srcx, srcy = move.src_xy
            destx, desty = move.dst_xy

            # Update last_board
            self._last_board = list(self._board)

            # Move
            self._board[destx][desty] = self._board[srcx][srcy]
            self.pop(xy_to_algebraic(srcx, srcy))
            return True

        return False

    def peek(self, san: str, /) -> _Square:
        """Return either None or a ChessPiece object at the square specified by the notation"""
        if not validate_san(san, is_pos=True):
            raise InvalidSANError()

        x, y = algebraic_to_xy(san)
        return self._board[x][y]

    def pop(self, san: str, /) -> bool:
        """Clears a square on the board"""

        if not validate_san(san, is_pos=True):
            raise InvalidSANError()

        x, y = algebraic_to_xy(san)
        self._board[x][y] = None
        return True

    # Pre/post-game helpers -------------------

    @classmethod
    def from_fen(cls, fen: str, /) -> ChessBoard:
        """Builds a ChessBoard from a FEN-string"""
        return cls(*parse_fen(fen))

    def export_fen(self) -> str: ...

    def log_move(self, san: str) -> None:
        """Logs the last move"""
        if not validate_san(san):
            raise InvalidSANError("invalid SAN string -> logging of move failed")

        self._move_log.append(san)

    def save_log(self, path: Path):
        """Saves the move log to a file for postgame analysis"""
        with open(str(path / f"log_{datetime.now()}.txt"), "x") as f:
            f.write(" ".join(move for move in self._move_log))


__all__ = ["ChessBoard"]
