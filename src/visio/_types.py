_WHITE = "white"
_BLACK = "black"

_KING = "king"
_QUEEN = "queen"
_KNIGHT = "knight"
_BISHOP = "bishop"
_ROOK = "rook"
_PAWN = "pawn"

_VALID_PROMOS = {_QUEEN, _KNIGHT, _BISHOP, _ROOK}

from .piece import ChessPiece

type _Square = ChessPiece | None
type _BoardType = list[list[_Square]]  # noqa pyi047
