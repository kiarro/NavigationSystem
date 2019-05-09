# Problem: image opened only for reading (i think that)
# Find how to open in both direction or close and reopen


from tkinter import *
import tkinter as tk
from PIL import ImageTk
from tkinter.filedialog import *
from PIL import Image
import numpy

class Functions():
    def __init__(self):
        super().__init__()

    def rgb_to_hex(rgb):
        letters="a b c d e f".split()
        r1 = rgb[0] // 16
        if r1 > 9:
            r1 = letters[r1 - 10]
        r2 = rgb[0] % 16
        if r2 > 9:
            r2 = letters[r2 - 10]
        g1 = rgb[1] // 16
        if g1 > 9:
            g1 = letters[g1 - 10]
        g2 = rgb[1] % 16
        if g2 > 9:
            g2 = letters[g2 - 10]
        b1 = rgb[2] // 16
        if b1 > 9:
            b1 = letters[b1 - 10]
        b2 = rgb[2] % 16
        if b2 > 9:
            b2 = letters[b2 - 10]
        r1 = str(r1)
        r2 = str(r2)
        g1 = str(g1)
        g2 = str(g2)
        b1 = str(b1)
        b2 = str(b2)
        hex = "#" + r1 + r2 + g1 + g2 + b1 + b2
        return hex

    def rgb_to_hsv(rgb):
        # print(rgb)
        # print("\n")
        R = rgb[0]/255
        G = rgb[1]/255
        B = rgb[2]/255
        Cmax = max(R, G, B)
        Cmin = min(R, G, B)
        delta = Cmax-Cmin

        if Cmax == Cmin:
            H = 0
        elif Cmax == R:
            H = 60 * (((G - B) / delta) % 6)
        elif Cmax == G:
            H = 60 * (((B - R) / delta) + 2)
        elif Cmax == B:
            H = 60 * (((R - G) / delta) + 4)

        if Cmax == 0:
            S = 0
        else:
            S = delta/Cmax*100

        V = Cmax*100
        return (H, S, V)

    def hsv_to_rgb(hsv):
        # print(hsv)
        H = hsv[0]
        H = H % 360
        S = hsv[1] / 100
        V = hsv[2] / 100
        C = V*S
        X = C*(1-abs((H/60)%2 - 1))
        m = V - C
        H = H // 60
        # print(C)
        # print(X)
        if H == 0:
            rgb = (C, X, 0)
        elif H == 1:
            rgb = (X, C, 0)
        elif H == 2:
            rgb = (0, C, X)
        elif H == 3:
            rgb = (0, X, C)
        elif H == 4:
            rgb = (X, 0, C)
        else:
            rgb = (C, 0, X)
        # print(rgb)
        rgb = ((int)((rgb[0] + m)*255), (int)((rgb[1] + m)*255), (int)((rgb[2] + m)*255))
        return rgb


    def create_text_file_path(path1):
        path = ""
        l = 1
        droplets = path1.split("\\")
        for i in droplets:
            if l < len(droplets):
                path = path + i
                path = path + "\\"
            l = l + 1
        path = path + "Text_Map.txt"
        return path

    def fix_path(path1):
        path = ""
        l = 1
        droplets = path1.split("/")
        for i in droplets:
            path = path + i
            if l < len(droplets):
                path = path + "\\"
            l = l + 1
        return path

    def refact_pixel(color_rgb=None, color_hsv=None):
        h = 0
        if color_hsv == None:
            color_hsv = Functions.rgb_to_hsv(color_rgb)
        if color_hsv[0]>180 and color_hsv[0]<300:
            h = Functions.find_depth(color_hsv[1])
        else:
            h = 0
        return h

    def find_depth(color_h):
        h = (color_h-variables.color_min_hsv[1])\
            /(variables.color_max_hsv[1]-variables.color_min_hsv[1])
        h = h * (variables.depth_max - variables.depth_min) + variables.depth_min
        return h

    def sort_uprising(x):
        if len(x) == 1 or len(x) == 0:
            return x
        else:
            pivot = x[0]
            i = 0
            for j in range(len(x) - 1):
                if (x[j + 1])[1] < pivot[1]:
                    x[j + 1], x[i + 1] = x[i + 1], x[j + 1]
                    i += 1
            x[0], x[i] = x[i], x[0]
            first_part = Functions.sort_uprising(x[:i])
            second_part = Functions.sort_uprising(x[i + 1:])
            first_part.append(x[i])
            return first_part + second_part

    # def refact_map(self):
    #     text_map_file = open(variables.path_to_text_map, "w")
    #     for y in range(variables.image_height):
    #         for x in range(variables.image_width):
    #             num_h = Functions.refact_pixel(hsv=variables.image_in_hsv[x, y])
    #             num_h = num_h // 1
    #             text_map_file.write((str)((int)(num_h)))
    #             if x < map_width-1:
    #                 text_map_file.write("\t")
    #         if y < map_height-1:
    #             text_map_file.write("\n")
    #     text_map_file.close()

    def image_median_filter(filter_size=5):
        # new_image = Image.new('RGB', (variables.image_width, variables.image_height))  # Create empty matrix-sized image
        new_image = numpy.zeros(shape=(variables.image_height, variables.image_width),
                                             dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4')])
        a=[]
        for y in range(variables.image_height):
            for x in range(variables.image_width):
                a.clear()
                for j in range(filter_size):
                    for i in range(filter_size):
                        if x-filter_size//2+j>=0 and y-filter_size//2+i>=0 and x-filter_size//2+i<variables.image_width and y-filter_size//2+j<variables.image_height:
                            a.append(variables.image_in_hsv[y-filter_size//2+j, x-filter_size//2+i])
                        else:
                            if y-filter_size//2+j<0:
                                nearest_y = 0
                            elif y-filter_size//2+j>=variables.image_height:
                                nearest_y = variables.image_height-1
                            else:
                                nearest_y = y-filter_size//2+j

                            if x-filter_size//2+i<0:
                                nearest_x = 0
                            elif x-filter_size//2+i>=variables.image_width:
                                nearest_x = variables.image_width-1
                            else:
                                nearest_x = x-filter_size//2+i

                            a.append(variables.image_in_hsv[nearest_y, nearest_x])

                a = Functions.sort_uprising(a)
                print("{} is {} element".format(a[filter_size*filter_size//2], x))
                new_image[y, x] = a[filter_size*filter_size//2]
        return new_image

    # def image_median_filter(filter_size=3):
    #     # new_image = Image.new('RGB', (variables.image_width, variables.image_height))  # Create empty matrix-sized image
    #     new_image = numpy.zeros(shape=(variables.image_height, variables.image_width),
    #                                          dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4')])
    #     for y in range(variables.image_height):
    #         pixel_list = []
    #         for x in range(variables.image_width):
    #             if x == 0:
    #                 a = []
    #                 for j in range(filter_size):
    #                     for i in range(filter_size):
    #                         if y - filter_size // 2 + j < 0:
    #                             nearest_y = 0
    #                         elif y - filter_size // 2 + j >= variables.image_height:
    #                             nearest_y = variables.image_height - 1
    #                         else:
    #                             nearest_y = y - filter_size // 2 + j
    #
    #                         if x - filter_size // 2 + i < 0:
    #                             nearest_x = 0
    #                         elif x - filter_size // 2 + i >= variables.image_width:
    #                             nearest_x = variables.image_width - 1
    #                         else:
    #                             nearest_x = x - filter_size // 2 + i
    #
    #                         a.append(variables.image_in_hsv[nearest_y, nearest_x])
    #
    #                 pixel_list = a
    #                 pixel_list.sort(key=lambda s: s[1])
    #             else:
    #                 i = filter_size
    #                 for j in range(filter_size):
    #                     if y - filter_size // 2 + j < 0:
    #                         nearest_y = 0
    #                     elif y - filter_size // 2 + j >= variables.image_height:
    #                         nearest_y = variables.image_height - 1
    #                     else:
    #                         nearest_y = y - filter_size // 2 + j
    #
    #                     if x - filter_size // 2 + i < 0:
    #                         nearest_x = 0
    #                     elif x - filter_size // 2 + i >= variables.image_width:
    #                         nearest_x = variables.image_width - 1
    #                     else:
    #                         nearest_x = x - filter_size // 2 + i
    #
    #                     a.append(variables.image_in_hsv[nearest_y, nearest_x])
    #
    #                 j1 = 0
    #                 j2 = 0
    #                 for i in range(filter_size):
    #                     for j in range(filter_size*filter_size):
    #                         if a[i] == pixel_list[j]:
    #                             pixel_list.pop(j)
    #                             a.pop(i)
    #                             break
    #                     for j in range(filter_size*filter_size-1):
    #                         if a[filter_size*filter_size-i+filter_size-4-i][1] > pixel_list[j][1]:
    #                             pixel_list.insert(j, a[filter_size*filter_size-i+filter_size-1-i])
    #                             break
    #
    #
    #
    #             print("{} is {} element".format(pixel_list[4], x))
    #             new_image[y, x] = pixel_list[4]
    #     return new_image



class Flags():
    def __init__(self):
        super().__init__()
        self.init_flags()

    def init_flags(self):
        self.flag_setting_color_max = False
        self.flag_setting_color_min = False

class Variables():
    def __init__(self):
        super().__init__()
        self.init_variables()

    def init_variables(self):
        self.color_max = (255, 255, 255, 255)
        self.color_min = (255, 255, 255, 255)
        self.color_max_hsv = (255, 255, 255)
        self.color_min_hsv = (255, 255, 255)
        self.depth_max = 100
        self.depth_min = 1
        self.path_to_text_map = ""
        self.path_to_image_map = ""
        self.image_height = 0 # высота
        self.image_width = 0 # ширина
        self.opened_for_using_image = None
        self.image_in_hsv = None

class Windows():
    def __init__(self):
        super().__init__()

    main_window = None
    set_color_window = None

class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.init_main()

    def init_main(self):
        windows.main_window = self

        self.toolbar = tk.Frame(bg="#d7d8e0", bd=2, height=140, width=140)

        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.open_img = tk.PhotoImage(file="open.gif")
        self.btn_open_dialog = tk.Button(self.toolbar, text="Choose map", command=self.open_image,
                                    bg="#d7d8e0", bd=0, compound=tk.TOP, image=self.open_img)
        self.btn_open_dialog.pack(side=tk.LEFT)

        self.color_img = tk.PhotoImage(file="color.gif")
        self.btn_color_dialog = tk.Button(self.toolbar, text="Choose color", command=self.open_dialog_to_choose_color,
                                    bg="#d7d8e0", bd=0, compound=tk.TOP, image=self.color_img)
        self.btn_color_dialog.pack(side=tk.LEFT)

        self.refact_img = tk.PhotoImage(file="refact.gif")
        self.btn_refact = tk.Button(self.toolbar, text="Refact map", command=self.refact_map,
                                         bg="#d7d8e0", bd=0, compound=tk.TOP, image=self.refact_img)
        self.btn_refact.pack(side=tk.LEFT)

        self.filter_img = tk.PhotoImage(file="filter.gif")
        self.btn_filter = tk.Button(self.toolbar, text="Filter out map", command=self.create_and_display_median_filtered_image,
                                    bg="#d7d8e0", bd=0, compound=tk.TOP, image=self.filter_img)
        self.btn_filter.pack(side=tk.LEFT)

        self.canvas = Canvas(root, height=984, width=800, scrollregion=(0,0,variables.image_width,variables.image_height))
        self.hbar = Scrollbar(root, orient=HORIZONTAL)
        self.hbar.pack(side=BOTTOM, fill=X)
        self.hbar.config(command=self.canvas.xview)
        self.vbar = Scrollbar(root, orient=VERTICAL)
        self.vbar.pack(side=RIGHT, fill=Y)
        self.vbar.config(command=self.canvas.yview)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.canvas.pack(side=tk.TOP, fill=BOTH)
        self.canvas.bind("<Button-1>", self.mouse1_handler)

    def open_image(self):
        # Tk().withdraw()
        filename = askopenfilename()

        # #
        # a = [9,9,3,6,1,0,8,9,2]
        # a=Functions.sort_uprising(a)
        # for i in range(9):
        #     print(a[i])
        # #

        if not filename == "":
            variables.path_to_image_map = Functions.fix_path(filename)
            variables.path_to_text_map = Functions.create_text_file_path(variables.path_to_image_map)
            self.opened_img = Image.open(variables.path_to_image_map)
            variables.opened_for_using_image = self.opened_img.load()
            variables.image_width, variables.image_height = self.opened_img.size
            # print("path to file is {}".format(variables.path_to_image_map))

            variables.image_in_hsv = numpy.zeros(shape=(variables.image_height, variables.image_width), dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4')])
            for i in range(variables.image_height):
                for j in range(variables.image_width):
                    variables.image_in_hsv[i, j] = Functions.rgb_to_hsv(variables.opened_for_using_image[j, i])
            # print(variables.image_in_hsv)

            self.draw_image(img=self.opened_img)

    def open_dialog_to_choose_color(self):
        self.dialog_to_choose_color = Dialog_to_choose_color(self)

    def draw_image(self, img):
        self.n_img = ImageTk.PhotoImage(img)
        self.canvas.config(scrollregion = (0, 0, variables.image_width, variables.image_height))
        imagesprite = self.canvas.create_image(variables.image_width/2, variables.image_height/2, image=self.n_img)

    def create_and_display_median_filtered_image(self):
        # d = [(120, 120, 120), (200, 120, 120), (120, 120, 200), (120, 50, 120), (0, 0, 120), (120, 0, 120),
        #      (120, 120, 80), (80, 50, 120), (220, 0, 50)]
        # s = Functions.sort_uprising(d)
        # print(s)
        # for i in range(9):
        #     print(Functions.rgb_to_hsv(s[i])[1])

        # before code works

        variables.image_in_hsv = Functions.image_median_filter()
        for i in range(variables.image_height):
            for j in range(variables.image_width):
                self.opened_img.putpixel((j, i), Functions.hsv_to_rgb(variables.image_in_hsv[i, j]))
        self.draw_image(img=self.opened_img)

    def mouse1_handler(self, event):
        # s = root.geometry()
        # s = s.split('+')
        # print("Окно находится на позиции х={} y={}".format(s[1], s[2]))
        # x = self.winfo_pointerx() - (int)(s[1])
        # y = self.winfo_pointery() - (int)(s[2])
        x = event.x
        y = event.y
        if flags.flag_setting_color_max:
            variables.color_max = variables.opened_for_using_image[int(x+self.hbar.get()[0]*variables.image_width), int(y+self.vbar.get()[0]*variables.image_height)]
            variables.color_max_hsv = variables.image_in_hsv[int(y+self.vbar.get()[0]*variables.image_height),int(x+self.hbar.get()[0]*variables.image_width)]
            flags.flag_setting_color_max = False
            print("Цвет позиции = {}".format(variables.color_max))
            print("Цвет позиции = {}".format(Functions.rgb_to_hsv(variables.color_max)))
            windows.set_color_window.col_1["bg"]=Functions.rgb_to_hex(variables.color_max)
        if flags.flag_setting_color_min:
            variables.color_min = variables.opened_for_using_image[int(x+self.hbar.get()[0]*variables.image_width), int(y+self.vbar.get()[0]*variables.image_height)]
            variables.color_min_hsv = variables.image_in_hsv[int(y+self.vbar.get()[0]*variables.image_height), int(x+self.hbar.get()[0]*variables.image_width)]
            flags.flag_setting_color_min = False
            print("Цвет позиции = {}".format(variables.color_min))
            windows.set_color_window.col_2["bg"]=Functions.rgb_to_hex(variables.color_min)
        print("Курсор находится на позиции х={} y={}".format(int(x+self.hbar.get()[0]*variables.image_width), int(y+self.vbar.get()[0]*variables.image_height)))

    def refact_map(self):
        text_map_file = open(variables.path_to_text_map, "w")
        for y in range(variables.image_height):
            for x in range(variables.image_width):
                num_h = Functions.refact_pixel(color_hsv=variables.image_in_hsv[y, x])
                num_h = num_h // 1
                text_map_file.write((str)((int)(num_h)))
                if x < variables.image_width-1:
                    text_map_file.write("\t")
            if y < variables.image_height-1:
                text_map_file.write("\n")
        text_map_file.close()

class Dialog_to_choose_color(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.init_child()

    def init_child(self):
        windows.set_color_window = self

        self.title("Color settings")
        self.geometry("500x150+300+400")
        self.resizable(False, False)

        # Create bar for set max depth

        self.enter_color1_tools = tk.Frame(self, bg="#d7d8e0", bd=2, height=300, width=200)
        self.enter_color1_tools.pack(side=tk.TOP, fill=tk.X)

        self.t1_1 = Label(self.enter_color1_tools, text='Enter max depth: ')
        self.t1_1.config(font=('Verdana', 12),  bg="#d7d8e0")
        self.t1_1.pack(side=tk.LEFT)

        self.win_1 = Entry(self.enter_color1_tools, width=5)
        self.win_1.config(font=('Verdana', 12))
        self.win_1.pack(side=tk.LEFT)

        self.t1_2 = Label(self.enter_color1_tools, text='   Enter max color: ')
        self.t1_2.config(font=('Verdana', 12), bg="#d7d8e0")
        self.t1_2.pack(side=tk.LEFT)

        self.no_img1 = tk.PhotoImage(file="no_image.gif")
        self.col_1 = Button(self.enter_color1_tools, text=" ", command=self.invert_setting_color_max,
                       bg=Functions.rgb_to_hex(variables.color_max), bd=2, compound=tk.LEFT, width=50, height=25,
                       image=self.no_img1)
        self.col_1.pack(side=tk.LEFT)

        # Create bar for set min depth

        self.enter_color2_tools = tk.Frame(self, bg="#d7d8e0", bd=2, height=300, width=200)
        self.enter_color2_tools.pack(side=tk.TOP, fill=tk.X)

        self.t2_1 = Label(self.enter_color2_tools, text='Enter min depth: ')
        self.t2_1.config(font=('Verdana', 12), bg="#d7d8e0")
        self.t2_1.pack(side=tk.LEFT)

        self.win_2 = Entry(self.enter_color2_tools, width=5)
        self.win_2.config(font=('Verdana', 12))
        self.win_2.pack(side=tk.LEFT)

        self.t2_2 = Label(self.enter_color2_tools, text='   Enter min color: ')
        self.t2_2.config(font=('Verdana', 12), bg="#d7d8e0")
        self.t2_2.pack(side=tk.LEFT)

        self.no_img2 = tk.PhotoImage(file="no_image.gif")
        self.col_2 = Button(self.enter_color2_tools, text=" ", command=self.invert_setting_color_min,
                            bg=Functions.rgb_to_hex(variables.color_min), bd=2, compound=tk.LEFT, width=50, height=25,
                            image=self.no_img2)
        self.col_2.pack(side=tk.LEFT)

        # Create bar for main button

        self.button_bar = tk.Frame(self, bg="#d7d8e0", bd=2, height=300, width=200)
        self.button_bar.pack(side=tk.TOP, fill=tk.X)

        self.no_img3 = tk.PhotoImage(file="no_image.gif")
        self.button_Ok = Button(self.button_bar, text="Ok", command=self.close,
                            bg="#d7d8e0", bd=2, compound=tk.LEFT, width=50, height=50,
                            image=self.no_img3)
        self.button_Ok.pack()

        self.mainloop()

    def invert_setting_color_max(self):
        if flags.flag_setting_color_max:
            flags.flag_setting_color_max = False
        else:
            flags.flag_setting_color_max = True

    def invert_setting_color_min(self):
        if flags.flag_setting_color_min:
            flags.flag_setting_color_min = False
        else:
            flags.flag_setting_color_min = True

    def close(self):
        variables.depth_max = (int)(self.win_1.get())
        variables.depth_min = (int)(self.win_2.get())
        variables.color_max_hsv = Functions.rgb_to_hsv(variables.color_max)
        variables.color_min_hsv = Functions.rgb_to_hsv(variables.color_min)
        self.destroy()
        print("Max depth = {}, Min depth = {}".format(variables.depth_max, variables.depth_min))


if __name__ == "__main__":
    root = tk.Tk()
    flags = Flags()
    variables = Variables()
    windows = Windows()
    app = Main(root)
    app.pack()
    root.title("Map Refactor")
    root.geometry("1024x800+200+100")

    root.mainloop()


