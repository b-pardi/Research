import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector

# generate some sample data
t = np.arange(0.0, 10.0, 0.1)
y1 = np.sin(2*np.pi*t)
y2 = np.cos(2*np.pi*t)

# create two subplots
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

# plot the data on each subplot
ax1.plot(t, y1)
ax2.plot(t, y2)

# create a SpanSelector for each subplot
span1 = SpanSelector(ax1, onselect=lambda xmin, xmax: span_changed(xmin, xmax, span2), props=dict(alpha=0.5, facecolor='red'), direction='horizontal', interactive=True)
span2 = SpanSelector(ax2, onselect=lambda xmin, xmax: span_changed(xmin, xmax, span1), props=dict(alpha=0.5, facecolor='blue'), direction='horizontal', interactive=True)

# define a function to handle span changes
def span_changed(xmin, xmax, other_span):
    other_span.span = xmin, xmax
    other_span.rect.set_x(xmin)
    other_span.rect.set_width(xmax - xmin)
    fig.canvas.draw()

# show the plot
plt.show()
