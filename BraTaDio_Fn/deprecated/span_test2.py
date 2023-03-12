import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
import inspect
from pprint import pprint

# define a function to handle span selection events
def onselect(xmin, xmax):
    for span in spans:
        if span.active:
            span.extents = (xmin, xmax)
            #span.draw()
            #pprint(inspect.getmembers(span))
            with open('span_mems.txt', 'w') as file:
                for line in inspect.getmembers(span):
                    file.writelines(str(line))
                    file.write('\n')

# generate some sample data
x = range(50)
y1 = [i**2 for i in x]
y2 = [i*10 for i in x]

# create the subplots
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

# plot the data on each subplot
ax1.plot(x, y1)
ax2.plot(x, y2)

# add a span selector to each subplot
spans = []
span1 = SpanSelector(ax1, onselect, 'horizontal', useblit=True,
                     props=dict(alpha=0.5, facecolor='red'), interactive=True)
spans.append(span1)
span2 = SpanSelector(ax2, onselect, 'horizontal', useblit=True,
                     props=dict(alpha=0.5, facecolor='blue'), interactive=True)
spans.append(span2)

plt.show()
