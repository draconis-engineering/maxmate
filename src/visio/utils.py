from collections.abc import Callable, Sequence

from src.visio.san_fen import validate_san


def _require_int(o: Sequence[object], func: Callable) -> None:
    for i in o:
        if not isinstance(i, int) or isinstance(i, bool):
            raise TypeError(f"function {func.__name__} requires integers")


COO_MAPPING: dict[str, int] = {
    "a": 1,
    "b": 2,
    "c": 3,
    "d": 4,
    "e": 5,
    "f": 6,
    "g": 7,
    "h": 8,
}

R_COO_MAPPING: dict[int, str] = {
    1: "a",
    2: "b",
    3: "c",
    4: "d",
    5: "e",
    6: "f",
    7: "g",
    8: "h",
}


def xy_to_algebraic(x: int, y: int) -> str:
    _require_int([x, y], xy_to_algebraic)
    if 0 > x or x > 8 or 0 > y or x > 8:
        raise ValueError("X and Y must be in between 1 and 8 inclusive")
    pos_san = R_COO_MAPPING[x] + str(y)
    validate_san(pos_san, is_pos=True)
    return pos_san


def algebraic_to_xy(san: str) -> tuple[int, int]:
    validate_san(san, is_pos=True)
    return COO_MAPPING[san[0]], int(san[1])
