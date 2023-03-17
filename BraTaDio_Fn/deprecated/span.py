import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector

fig = plt.figure(figsize=(8, 6))
yax = fig.add_subplot(1,2,1)
ax1 = fig.add_subplot(2,2,1)
ax2 = fig.add_subplot(2,2,3)
axz1 = fig.add_subplot(2,2,2)
axz2 = fig.add_subplot(2,2,4)


x = np.arange(0.0, 5.0, 0.01)
y1 = np.sin(2*np.pi*x) + 0.5*np.random.randn(len(x))
y2 = np.cos(2*np.pi*x) + 0.5*np.random.randn(len(x))

ax1.plot(x, y1, '-')
ax2.plot(x, y2, '-')
ax1.set_ylim(-2, 2)
ax2.set_ylim(-2, 2)
yax.set_title('meta')
ax1.set_title('sin')
ax2.set_title('cos')

line_sin, = axz1.plot(x, y2, '-')
line_cos, = axz2.plot(x, y2, '-')


def onselect1(xmin, xmax):
    indmin, indmax = np.searchsorted(x, (xmin, xmax))
    indmax = min(len(x) - 1, indmax)

    thisx = x[indmin:indmax]
    thisy1 = y1[indmin:indmax]
    line_sin.set_data(thisx, thisy1)
    axz1.set_xlim(thisx[0], thisx[-1])
    axz1.set_ylim(thisy1.min(), thisy1.max())
    span2.horizontal_span.set_bounds(xmin, xmax)
    fig.canvas.draw_idle()

    # save
    #np.savetxt("text.out", np.c_[thisx, thisy])

def onselect2(xmin, xmax):
    indmin, indmax = np.searchsorted(x, (xmin, xmax))
    indmax = min(len(x) - 1, indmax)
    
    thisx = x[indmin:indmax]
    thisy2 = y2[indmin:indmax]
    line_cos.set_data(thisx, thisy2)
    axz2.set_xlim(thisx[0], thisx[-1])
    axz2.set_ylim(thisy2.min(), thisy2.max())
    span1.horizontal_span.set_bounds(xmin, xmax)
    fig.canvas.draw_idle()

# set useblit True on gtkagg for enhanced performance
span1 = SpanSelector(ax1, onselect1, 'horizontal', useblit=True,
                    props=dict(alpha=0.5, facecolor='red'),
                    interactive=True, drag_from_anywhere=True)

span2 = SpanSelector(ax2, onselect2, 'horizontal', useblit=True,
                    props=dict(alpha=0.5, facecolor='red'),
                    interactive=True, drag_from_anywhere=True)



plt.show()