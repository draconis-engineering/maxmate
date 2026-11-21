class Move:
    def __init__(self, src, dest, promo=None):
        """
        src is Square representing source square
        dst is Square representing destination square
        promo is Piece representing promotion
        """
        self.src = src
        self.dest = dest
        self.promo = promo

    def __str__(self):
        if self.promo:
            return f"{self.src!s} -> {self.dest!s} = {self.promo.name}"
        else:
            return f"{self.src!s} -> {self.dest!s}"
