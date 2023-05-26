import tkinter as tk

app = tk.Tk()
fr=tk.Frame(app)
fr.grid(rowspan=2, columnspan=2)

# this represents what you have in the page above
something_large = tk.Button(fr, text="HELLO WORLD")
something_large_too = tk.Button(fr, text="Hello world")
something_large.grid(row=0, column=0)
something_large_too.grid(row=0, column=1)

bottom_frame = tk.Frame(fr)
bottom_frame.grid(row=1, columnspan=2)
b=tk.Button(bottom_frame,text='1')
b.grid(row=0, column=0)
b1=tk.Button(bottom_frame,text='2')
b1.grid(row=0, column=1,)
b2=tk.Button(bottom_frame,text='3')
b2.grid(row=0, column=2)
b3=tk.Button(bottom_frame,text='4')
b3.grid(row=0, column=3)
app.mainloop()