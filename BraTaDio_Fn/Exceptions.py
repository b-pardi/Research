class ShapeMismatchException(Exception):
    def __init__(self, shapes, msg):
        self.shapes = shapes
        if msg:
            self.msg = msg
        else:
            self.msg = None

    def __str__(self):
        if self.msg:
            return f"SHAPE MISMATCH ERROR CAUGHT: {self.msg}\nDims must be equal, found {self.shapes[0]} and {self.shapes[1]}"
        else:
            return "SHAPE MISMATCH ERROR CAUGHT"