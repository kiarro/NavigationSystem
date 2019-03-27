def vvod():
    global maxdep, maxmass
    maxdep = win_1.get()
    maxmass = win_2.get()

def close_window():
    window.destroy()

def btn_func():
    vvod()
    close_window()


from tkinter import *
window = Tk()
window.geometry("300x100")

t1 = Label(window, text='Enter max depth, please')
t1.config(font=('Verdana', 8))
t1.pack()

win_1 = Entry(window, width=20)
win_1.pack()

t2 = Label(window, text='Enter max mass, please')
t2.config(font=('Verdana', 8))
t2.pack()

win_2 = Entry(window, width=20)
win_2.pack()

btn = Button(window, text='ok', command=btn_func)
btn.pack()

window.mainloop()

print(maxdep)
print(maxmass)

from tkinter import Tk
from tkinter.filedialog import askopenfilename
Tk().withdraw()
filename = askopenfilename()

print(filename)

