from .board import ChessBoard


class Engine:
    def __init__(self) -> None:
        self._instance = ChessBoard()
