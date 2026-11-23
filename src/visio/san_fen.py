import re

from ._types import (
    _BISHOP,
    _BLACK,
    _KING,
    _KNIGHT,
    _PAWN,
    _QUEEN,
    _ROOK,
    _WHITE,
    _BoardType,
    _Square,
)
from .exceptions import InvalidFENError as _InvalidFENError
from .piece import ChessPiece as _ChessPiece

# ==========================================
# SAN Notation / / / / / / / / / / / / / / /
# ==========================================

SAN_PLACEMENT_ONLY_REGEX = re.compile(r"^[a-h][1-8]$")

SAN_REGEX = re.compile(
    r"^(?:"
    r"O-O(?:-O)?"  # Castling (kingside or queenside)
    r"|"
    r"[KQRBN]?"  # Piece (omitted for pawns)
    r"[a-h]?[1-8]?"  # Optional file/rank disambiguation
    r"x?"  # Optional capture indicator
    r"[a-h][1-8]"  # Destination square
    r"(?:=[QRBN])?"  # Optional pawn promotion
    r")"
    r"[+#]?$"  # Optional check (+) or checkmate (#)
)


def validate_san(move: str, *, is_pos: bool = False) -> bool:
    if is_pos:
        return bool(SAN_PLACEMENT_ONLY_REGEX.match(move.strip()))
    return bool(SAN_REGEX.match(move.strip()))


# ==========================================
# FEN Notation / / / / / / / / / / / / / / /
# ==========================================

# Board, active color, castling rights, en passant avaliability, half moves, full moves
_DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
_FEN_TO_PIECE: dict[str, _ChessPiece] = {
    "P": _ChessPiece(_PAWN, _WHITE),
    "N": _ChessPiece(_KNIGHT, _WHITE),
    "B": _ChessPiece(_BISHOP, _WHITE),
    "R": _ChessPiece(_ROOK, _WHITE),
    "Q": _ChessPiece(_QUEEN, _WHITE),
    "K": _ChessPiece(_KING, _WHITE),
    "p": _ChessPiece(_PAWN, _BLACK),
    "n": _ChessPiece(_KNIGHT, _BLACK),
    "b": _ChessPiece(_BISHOP, _BLACK),
    "r": _ChessPiece(_ROOK, _BLACK),
    "q": _ChessPiece(_QUEEN, _BLACK),
    "k": _ChessPiece(_KING, _BLACK),
}


def validate_fen(fen: str, /) -> None:
    parts = fen.split()
    if len(parts) != 6:
        raise _InvalidFENError(f"a FEN string needs 6 parts, not {len(parts)}")

    placement, turn, castling, ep, halfmove, fullmove = parts

    # Validate piece placement
    ranks = placement.split("/")
    if len(ranks) != 8:
        raise _InvalidFENError(f"FEN string ranks needs 8 parts, not {len(ranks)}")

    # Validate board
    valid_pieces = set("prnbqkPRNBQK")
    for rank in ranks:
        square_count = 0
        for char in rank:
            if char.isdigit() and "1" <= char <= "8":  # Theres no way this is right
                square_count += int(char)
            elif char in valid_pieces:
                square_count += 1
            else:
                raise _InvalidFENError(f"Unknown chess character: {char}")
        if square_count != 8:
            raise _InvalidFENError(f"Invalid board dimension: {square_count}")

    # Validate active color
    if turn not in {"w", "b"}:
        raise _InvalidFENError(f"Invalid chess color: {turn}")

    # Validate castling availability
    if not re.fullmatch(r"-|K?Q?k?q?", castling):
        raise _InvalidFENError(f"Invalid castling configuration: {castling}")

    # Validate en passant target square
    if not re.fullmatch(r"-|[a-h][36]", ep):
        raise _InvalidFENError(f"Invalid en passant configuration: {ep}")

    # Validate halfmove clock and fullmove number
    if not halfmove.isdigit() and fullmove.isdigit() and int(fullmove) >= 1:
        raise _InvalidFENError(
            f"Invalid halfmove/fullmove counts: {halfmove}, {fullmove}"
        )

    if placement.count("K") != 1 or placement.count("k") != 1:
        raise _InvalidFENError("king(s) is missing")


def _build_row_from_fen_rank(rank: str, /) -> list[_Square]:
    row: list[_Square] = []
    for char in rank:
        if char.isdigit():
            row.extend([None] * int(char))
        else:
            row.append(_FEN_TO_PIECE[char])

    return row


def build_board_from_fen(fen: str, /) -> _BoardType:
    validate_fen(fen)
    piece_placement = fen.split()[0]
    ranks = piece_placement.split("/")

    board: _BoardType = [_build_row_from_fen_rank(rank) for rank in ranks]

    return board


def parse_fen(fen: str, /) -> tuple[_BoardType, str, str, str, int, int]:
    validate_fen(fen)
    board, active, castling, ep, half, full = fen.strip().split()

    return (build_board_from_fen(board), active, castling, ep, int(half), int(full))
