from __future__ import annotations

from src.visio.exceptions import InvalidSANError
from src.visio.piece import ChessPiece
from src.visio.utils import algebraic_to_xy, validate_within_bounds, xy_to_algebraic

from ._types import _BLACK, _WHITE
from .san_fen import validate_san


class Move:
    def __init__(self, src: str, dst: str, promo: ChessPiece | None = None):
        """src and dst are algebraic notation strings representing squares
        promo is a ChessPiece representing promotion
        """
        if not validate_san(src, is_pos=True):
            raise InvalidSANError(f"{src} is invalid SAN")

        if not validate_san(dst, is_pos=True):
            raise InvalidSANError(f"{dst} is invalid SAN")

        self.src = src
        self.dst = dst
        self.promo = promo

    def to_san(self) -> str: ...

    @property
    def src_xy(self) -> tuple[int, int]:
        return algebraic_to_xy(self.src)

    @property
    def dst_xy(self) -> tuple[int, int]:
        return algebraic_to_xy(self.dst)

    @classmethod
    def from_xy(cls, srcx: int, srcy: int, dstx: int, dsty: int) -> Move:
        validate_within_bounds([srcx, srcy, dstx, dsty], 0, 7)
        return Move.from_xy(srcx, srcy, dstx, dsty)

    @classmethod
    def from_san(cls, san: str, board, /) -> Move:
        validate_san(san)
        return NotImplemented

    def __str__(self):
        if self.promo:
            return f"{self.src!s} -> {self.dst!s} = {self.promo.name}"
        else:
            return f"{self.src!s} -> {self.dst!s}"


def recursive_directional_fetch(
    x: int,
    y: int,
    dx: int,
    dy: int,
    moves: list[Move],
    board,
    color: str,
) -> list[Move]:
    """Recursively retrieves pseudolegal sliding moves along a single direction. `board` is a `ChessBoard` but importing for typing breaks"""
    nx, ny = x + dx, y + dy

    if color not in {_WHITE, _BLACK}:
        raise ValueError(f"unknown color: {color}")

    if not validate_within_bounds([nx, ny], 0, 7):
        return moves

    target = board.peek(xy_to_algebraic(nx, ny))
    from_sq = xy_to_algebraic(x, y)
    to_sq = xy_to_algebraic(nx, ny)

    if target is None:
        moves.append(Move(from_sq, to_sq))
        return recursive_directional_fetch(nx, ny, dx, dy, moves, board, color)

    if target._color != color:
        moves.append(Move(from_sq, to_sq))

    return moves


def pawn_moves(
    x: int,
    y: int,
    color: str,
    *,
    is_attacking: bool = False,
    promo: ChessPiece | None = None,
) -> list[Move]:
    """Returns the possible pseudo-legal moves that the pawn can take.
    Does not take into account current board state; That's `get_legal_moves()`'s job.
    SAN Validation is taken care of by `xy_to_algebraic()`"""

    if color not in {_BLACK, _WHITE}:
        raise ValueError(f"invalid color: {color}")

    moves: list[Move] = []
    src = xy_to_algebraic(x, y)

    # White moves up (+y), Black moves down (-y)
    direction = 1 if color == _WHITE else -1
    start_rank = 1 if color == _WHITE else 6
    promo_rank = 7 if color == _WHITE else 0

    next_y = y + direction

    # Stop if the pawn is already on the edge of the board
    if not (0 <= next_y <= 7):
        return moves

    # Only include promotion piece if landing on the final rank
    applied_promo = promo if next_y == promo_rank else None

    # Attacking squares (used for threat maps / captures)
    if is_attacking:
        for dx in (-1, 1):
            next_x = x + dx
            if 0 <= next_x <= 7:
                moves.append(
                    Move(
                        src=src,
                        dst=xy_to_algebraic(next_x, next_y),
                        promo=applied_promo,
                    )
                )
        return moves

    # Standard 1-square forward move
    moves.append(
        Move(
            src=src,
            dst=xy_to_algebraic(x, next_y),
            promo=applied_promo,
        )
    )

    # Starting 2-square forward move
    if y == start_rank:
        moves.append(
            Move(
                src=src,
                dst=xy_to_algebraic(x, y + (2 * direction)),
                promo=None,
            )
        )

    return moves


def rook_moves(x: int, y: int) -> list[Move]: ...
def knight_moves(x: int, y: int) -> list[Move]: ...
def bishop_moves(x: int, y: int) -> list[Move]: ...
def queen_moves(x: int, y: int) -> list[Move]: ...


def king_moves(x: int, y: int, board, color: str) -> list[Move]:
    if color not in {_WHITE, _BLACK}:
        raise ValueError(f"invalid color: {color}")

    nxs, nys = (
        (x - 1, x, x + 1, x - 1, x + 1, x - 1, x, x + 1),
        (y + 1, y + 1, y + 1, y, y, y - 1, y - 1, y - 1),
    )

    moves = [Move.from_xy(x, y, nx, ny) for nx, ny in zip(nxs, nys)]

    ### needs fixing
    for move in moves:
        trgt_sqr = board.peek(move.dst)
        if trgt_sqr is None:
            continue  # valid
        if trgt_sqr.color != color:
            continue
    return moves
