import matplotlib
matplotlib.use('TkAgg')  # Set the backend to TkAgg

import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
import numpy as np
import tkinter as tk
from tkinter import ttk

def update_text(event):
    text = text_entry.get()
    try:
        start, end = map(float, text.split(','))
        ax.set_xlim(start, end)
        fig.canvas.draw()
    except ValueError:
        print("Invalid input format. Please enter a valid range.")

def onselect(xmin, xmax):
    ax.set_xlim(xmin, xmax)
    text_entry.delete(0, tk.END)
    text_entry.insert(0, f"{xmin:.2f},{xmax:.2f}")
    fig.canvas.draw()

# Generate some data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create the plot
fig, ax = plt.subplots()
line, = ax.plot(x, y)

# Create the GUI window
root = tk.Tk()
root.title("Figure with Text Entry and Span Selector")

# Create the text entry widget
text_entry = ttk.Entry(root)
text_entry.bind('<Return>', update_text)
text_entry.pack()

# Create the span selector
span_selector = SpanSelector(ax, onselect, 'horizontal', useblit=True,
                             props={'alpha': 0.5, 'facecolor': 'red'})

# Embed the Matplotlib figure into the window
canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack()

# Start the GUI event loop
root.mainloop()
