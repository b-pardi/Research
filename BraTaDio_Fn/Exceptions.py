class ShapeMismatchException(Exception):
    def __init__(self, shapes, msg):
        self.shapes = shapes if shapes else (0,0)
        self.msg = msg if msg else None

    def __str__(self):
        if self.msg:
            return f"SHAPE MISMATCH ERROR CAUGHT: {self.msg}\nDims must be equal, found {self.shapes[0]} and {self.shapes[1]}"
        else:
            return "SHAPE MISMATCH ERROR CAUGHT"
        
class MissingPlotCustomizationException(Exception):
    def __init__(self, opt, msg):
        self.missing_option = opt if opt else ''
        self.msg = msg if msg else None
        
    def __str__(self):
        if self.msg:
            return f"PLOT CUSTOMIZATION ERROR CAUGHT: {self.msg}\nMissing input for field: {self.missing_option}"
        else:
            return "PLOT CUSTOMIZATION ERROR CAUGHT"