# Centi_ cost to avoid floating point math
# High king cost to tell the engine its priceless
_COSTS = {
    "pawn": 100,
    "knight": 300,
    "bishop": 300,
    "rook": 500,
    "queen": 900,
    "king": 1000000,
}


class ChessPiece:
    def __init__(self, name: str, color: str) -> None:
        self._name = name
        self._color = color
        self._cost = _COSTS[name]

    def __eq__(self, other: object, /) -> bool:
        return (
            isinstance(other, ChessPiece)
            and self._name == other._name
            and self._color == other._color
        )

    def __repr__(self) -> str:
        return ""
