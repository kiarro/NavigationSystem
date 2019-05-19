# подключаем библиотеки
from tkinter import *
import tkinter.ttk as ttk
from PIL import Image, ImageTk
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import numpy
import os

import Graph
import TransformMatrix
import RoutePlanning
import MapRefactor

picture = 'inception'  # глобальные переменные для имени картинки в главном окне
old_picture = '0'
txt_file_with_danger_of_heights = "DepthDangerZone.txt"
coordinates = [0, 0, 999, 999]
maxdep = 200
mindep = 50
# root = None

def btn_openMapRefactor():
    MapRefactor.startThis(root)

def btn_route():
    global curre
    os.remove(Graph.route_image)
    os.system('copy {} {}'.format(Graph.final_image, Graph.route_image))
    if current_algorithm == 'Simple':
        route = RoutePlanning.CreateRouteByTangents(coordinates[0], coordinates[1], coordinates[2], coordinates[3],
                                                       map_width, map_height, circle_array)
    elif current_algorithm == 'Tree':
        route = RoutePlanning.CreateRouteByTangentTree(coordinates[0], coordinates[1], coordinates[2], coordinates[3], map_width,
                                          map_height, circle_array)
    elif current_algorithm == 'Dijkstra':
        route = RoutePlanning.CreateRouteByDijkstraAlgorithm(coordinates[0], coordinates[1], coordinates[2], coordinates[3],
                                                       map_width, map_height, circle_array)
    print("Task complete: route was planed.")

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

def btn_parametrs():  # окно для параметров
    def vvod():
        global maxdep, mindep,coordinates
        maxdep = int(win_1.get())  # ввод значений
        mindep = int(win_2.get())
        coordinates[0] = int(win_x1.get())
        coordinates[1] = int(win_y1.get())
        coordinates[2] = int(win_x2.get())
        coordinates[3] = int(win_y2.get())

    def setDefault():
        global maxdep, mindep,coordinates
        win_1.insert(0, str(maxdep))
        win_2.insert(0, str(mindep))
        win_x1.insert(0, str(coordinates[0]))
        win_y1.insert(0, str(coordinates[1]))
        win_x2.insert(0, str(coordinates[2]))
        win_y2.insert(0, str(coordinates[3]))

    def close_window():  # закрытие окна по кнопке ok
        window.destroy()

    def btn_ok_func():
        vvod()
        close_window()

    def btn_cancel_func():
        close_window()

    window = Tk()
    window.geometry("300x130")    #300x100 на 300х150
    window.resizable(width=False, height=False)

    window.columnconfigure(0, pad=20)
    window.columnconfigure(1, pad=20)
    window.columnconfigure(2, pad=0)
    window.columnconfigure(3, pad=0)
    window.columnconfigure(4, pad=0)
    window.columnconfigure(5, pad=0)
    window.rowconfigure(0, pad=3)
    window.rowconfigure(1, pad=3)
    window.rowconfigure(2, pad=3)
    window.rowconfigure(3, pad=3)
    window.rowconfigure(4, pad=20)

    t1 = Label(window, text='Max depth')
    t1.config(font=('Verdana', 8))
    t1.grid(row=0, column=0)

    win_1 = Entry(window, width=8)
    win_1.grid(row=1, column=0)

    t2 = Label(window, text='Min depth')
    t2.config(font=('Verdana', 8))
    t2.grid(row=2, column=0)

    win_2 = Entry(window, width=8)
    win_2.grid(row=3, column=0)

    t_Points = Label(window, text="Points")
    t_Points.config(font=('Verdana', 8))
    t_Points.grid(row=0, column=1, columnspan=4)

    t_Point1 = Label(window, text="Start = [")
    t_Point1.config(font=('Verdana', 8))
    t_Point1.grid(row=1, column=1)

    win_x1 = Entry(window, width=8)
    win_x1.grid(row=1, column=2)

    t_G1 = Label(window, text=";")
    t_G1.config(font=('Verdana', 8))
    t_G1.grid(row=1, column=3)

    win_y1 = Entry(window, width=8)
    win_y1.grid(row=1, column=4)

    t_E1 = Label(window, text="]")
    t_E1.config(font=('Verdana', 8))
    t_E1.grid(row=1, column=5)

    t_Point2 = Label(window, text="  End = [")
    t_Point2.config(font=('Verdana', 8))
    t_Point2.grid(row=2, column=1)

    win_x2 = Entry(window, width=8)
    win_x2.grid(row=2, column=2)

    t_G2 = Label(window, text=";")
    t_G2.config(font=('Verdana', 8))
    t_G2.grid(row=2, column=3)

    win_y2 = Entry(window, width=8)
    win_y2.grid(row=2, column=4)

    t_E2 = Label(window, text="]")
    t_E2.config(font=('Verdana', 8))
    t_E2.grid(row=2, column=5)

    setDefault()

    btn_cancel = Button(window, text='cancel', command=btn_cancel_func)
    btn_cancel.grid(row=4, column=0, columnspan=2)

    btn_ok = Button(window, text='ok', command=btn_ok_func)
    btn_ok.grid(row=4, column=2, columnspan=4)


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
            global map_width, map_height, circle_array
            Graph.set_parameters(filename, mindep, maxdep)
            Graph.full_map_conjunction()
            print("Task complete: map was drew.")
            map_width, map_height = Graph.get_map_sizes()
            circle_array = TransformMatrix.transform_areas_to_circles(map_width, map_height, txt_file_with_danger_of_heights)
            Graph.draw_list_of_circles(circle_array, Graph.final_image)
            print("Task complete: circumferences were constructed.")


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

        routebtn = Button(self, text="Построить маршрут", height=1, width=20, command=btn_route)
        routebtn.grid(row=5, column=0)

        refactbtn = Button(self, text="JPEG -> Matrix", height=1, width=20, command=btn_openMapRefactor)
        refactbtn.grid(row=8, column=0)

        lbl2 = Label(self, text="Просмотр результатов:")
        lbl2.grid(row=13, column=0)  # надпись перед выпадающей кнопкой

        lbl3 = Label(self)  # область под выпадающую кнопку
        lbl3.grid(row=14, column=0)

        # выпадающая кнопка
        c = ttk.Combobox(lbl3, width=21)           #width=21 для  Windows 10
        c['values'] = ('Map', 'DangerDepthMask', 'Finale', 'Route')
        c.grid(column=0, row=1)

        def fun_im(self, *args):
            global old_picture, picture
            old_picture = picture
            picture = c.get()  # запись выбранного пользователем значения в переменную picture
            Draw()

        c.bind("<<ComboboxSelected>>", fun_im)  # считывание значения из выпадающей кнопки

        lbl4 = Label(self, text="Выбор алгоритма:")
        lbl4.grid(row=10, column=0)  # надпись перед выпадающей кнопкой

        lbl5 = Label(self, width=20)  # область под выпадающую кнопку
        lbl5.grid(row=11, column=0)

        # выпадающая кнопка
        c2 = ttk.Combobox(lbl5)  # width=21 для  Windows 10
        c2['values'] = ('Simple', 'Tree', 'Dijkstra')
        c2.grid(column=0, row=1)
        c2.current(0)
        global current_algorithm
        current_algorithm = c2.get()

        def fun_al(self, *args):
            global current_algorithm
            current_algorithm = c2.get()  # запись выбранного пользователем значения в переменную picture

        c2.bind("<<ComboboxSelected>>", fun_al)  # считывание значения из выпадающей кнопки



if __name__ == "__main__":
    # main создаем главное окно
    global root
    root = Tk()
    root.geometry("1000x500+100+100")
    root.title("SeaNavigationSystem")
    root.resizable(width=False, height=False)  # убирает возможностть масштабирования окна

    a = Menu(root)
    b = Drawn_fail(root)

    a.pack(side=LEFT)
    b.pack(side=RIGHT)

    root.mainloop()
