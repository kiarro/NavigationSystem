# подключаем библиотеки
from tkinter import *
import tkinter.ttk as ttk
from PIL import Image, ImageTk
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import numpy

import Graph
import TransformMatrix
import RoutePlanning

picture = 'inception'  # глобальные переменные для имени картинки в главном окне
old_picture = '0'
txt_file_with_danger_of_heights = "DepthDangerZone.txt"
coordinates = [0, 0, 999, 999]

def btn_parametrs():  # окно для параметров
    def vvod():
        global maxdep, mindep,coordinates
        maxdep = int(win_1.get())  # ввод значений
        mindep = int(win_2.get())
        xyxy = win_3.get()
        coordinates = xyxy.split()
        coordinates[0] = int(coordinates[0])
        coordinates[1] = int(coordinates[1])
        coordinates[2] = int(coordinates[2])
        coordinates[3] = int(coordinates[3])

    def close_window():  # закрытие окна по кнопке ok
        window.destroy()

    def btn_func():
        vvod()
        close_window()

    window = Tk()
    window.geometry("300x150")    #300x100 на 300х150
    window.resizable(width=False, height=False)

    t1 = Label(window, text='Enter max depth, please')
    t1.config(font=('Verdana', 8))
    t1.pack()

    win_1 = Entry(window, width=20)
    win_1.pack()

    t2 = Label(window, text='Enter min depth, please')
    t2.config(font=('Verdana', 8))
    t2.pack()

    win_2 = Entry(window, width=20)
    win_2.pack()

    t3 = Label(window, text='Xmin Ymin Xmax Ymax')
    t3.config(font=('Verdana', 8))
    t3.pack()

    win_3 = Entry(window, width=20)
    win_3.pack()

    btn = Button(window, text='ok', command=btn_func)
    btn.pack()


def btn_fail():  # окно для файла
    global filename
    Tk().withdraw()
    filename = askopenfilename()
    print(filename)

# root.attributes('-fullscreen', True)        #убирает все стандартные кнопки

class Drawn_fail(Frame):  # отрисовка файла в главном окне
    def __init__(self, master):
        Frame.__init__(self, master)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.original = Image.open(picture + '.png')  # сюда поступает значение переменной picture
        self.image = ImageTk.PhotoImage(self.original)
        self.display = Canvas(self, bd=0, highlightthickness=0, width=800, height=500)
        self.display.create_image(0, 0, image=self.image, anchor=NW, tags="IMG")
        self.display.grid(row=0, sticky=W + E + N + S)
        self.pack(fill=BOTH, expand=1)
        self.place(x=200, y=0)                #х = 160 на 200
        self.bind("<Configure>", self.resize)

    def resize(self, event):
        size = (event.width, event.height)
        resized = self.original.resize(size, Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(resized)
        self.display.delete("IMG")
        self.display.create_image(0, 0, image=self.image, anchor=NW, tags="IMG")


def Draw():  # функция для создания объекта с отрисовкой
    b = Drawn_fail(root)


class Menu(Frame):  # меню
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def Start(self, num):  # вызов функций Димы и Вани
        if num == 1:
            global map_width, map_height
            Graph.set_parameters(filename, mindep, maxdep)
            Graph.full_map_conjunction()
            print("Task complete: map was drew.")
            map_width, map_height = Graph.get_map_sizes()
            circle_array = TransformMatrix.transform_areas_to_circles(map_width, map_height, txt_file_with_danger_of_heights)
            print("Task complete: circumferences were constructed.")
            route = RoutePlanning.CreateRoute(coordinates[0], coordinates[1], coordinates[2], coordinates[3], map_width, map_height, circle_array)
            print("Task complete: route was planed.")

            Graph.draw_list_of_circles(circle_array)
            i_pr = route[0]
            lines = list()
            for i in route:
                lines.append([(int)(i_pr.x0 + (i_pr.r + 0.51) * numpy.cos(i_pr.a2)),
                              (int)(i_pr.y0 + (i_pr.r + 0.51) * numpy.sin(i_pr.a2)),
                              (int)(i.x0 + (i.r + 0.51) * numpy.cos(i.a1)),
                              (int)(i.y0 + (i.r + 0.51) * numpy.sin(i.a1))])
                i_pr = i
            Graph.draw_list_of_lines(lines)
            print("Task complete: route was drew.")

    def initUI(self):  # кнопки
        self.parent.title("Windows")
        self.pack(fill=BOTH, expand=True)

        lbl1 = Label(self, text="МЕНЮ")
        lbl1.grid(pady=4, padx=5)  # размеры области с текстом виндоус

        cbtn = Button(self, text="Параметры", height=1, width=20, command=btn_parametrs)
        cbtn.grid(row=2, column=0)

        hbtn = Button(self, text="Выбор файла", height=1, width=20, command=btn_fail)
        hbtn.grid(row=3, column=0)

        obtn = Button(self, text="Обработка", height=1, width=20, command=lambda: self.Start(1))
        obtn.grid(row=4, column=0)


        lbl2 = Label(self, text="Просмотр результатов:")
        lbl2.grid(row=5, column=0)  # надпись перед выпадающей кнопкой

        lbl3 = Label(self)  # область под выпадающую кнопку
        lbl3.grid(row=6, column=0)

        # выпадающая кнопка
        c = ttk.Combobox(lbl3, width=21)           #width=21 для  Windows 10
        c['values'] = ('DangerDepthMask', 'Finale', 'Map')
        c.grid(column=0, row=1)

        def fun(self, *args):
            global old_picture, picture
            old_picture = picture
            picture = c.get()  # запись выбранного пользователем значения в переменную picture
            Draw()

        c.bind("<<ComboboxSelected>>", fun)  # считывание значения из выпадающей кнопки

# main создаем главное окно
root = Tk()
root.geometry("1000x500+100+100")
root.resizable(width=False, height=False)  # убирает возможностть масштабирования окна

a = Menu(root)
b = Drawn_fail(root)

root.mainloop()
