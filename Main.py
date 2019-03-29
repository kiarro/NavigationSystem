from tkinter import *
import tkinter as tk
from PIL import ImageTk
from tkinter.filedialog import *
from PIL import Image

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

        V = Cmax

        return (H, S, V)

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

        self.canvas = Canvas(root, height=984, width=800)
        self.canvas.pack(side=tk.TOP, fill=tk.X)
        self.canvas.bind("<Button-1>", self.mouse1_handler)


    def open_image(self):
        # Tk().withdraw()
        filename = askopenfilename()
        variables.path_to_image_map = self.fix_path(filename)
        variables.path_to_text_map = self.create_text_file_path(variables.path_to_image_map)
        self.draw_image(img=variables.path_to_image_map)

    def open_dialog_to_choose_color(self):
        self.dialog_to_choose_color = Dialog_to_choose_color(self)

    def draw_image(self, img):
        self.opened_img = Image.open(img)
        self.opened_for_using_image = self.opened_img.load()
        self.n_img = ImageTk.PhotoImage(self.opened_img)
        img_height, img_width = self.opened_img.size
        imagesprite = self.canvas.create_image(img_height/2, img_width/2, image=self.n_img)

    def fix_path(self, path1):
        path = ""
        l = 1
        droplets = path1.split("/")
        for i in droplets:
            path = path + i
            if l < len(droplets):
                path = path + "\\"
            l = l + 1
        return path

    def create_text_file_path(self, path1):
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

    def mouse1_handler(self, event):
        # s = root.geometry()
        # s = s.split('+')
        # print("Окно находится на позиции х={} y={}".format(s[1], s[2]))
        # x = self.winfo_pointerx() - (int)(s[1])
        # y = self.winfo_pointery() - (int)(s[2])
        x = event.x
        y = event.y
        if flags.flag_setting_color_max:
            variables.color_max = self.opened_for_using_image[x, y]
            flags.flag_setting_color_max = False
            print("Цвет позиции = {}".format(variables.color_max))
            print("Цвет позиции = {}".format(Functions.rgb_to_hsv(variables.color_max)))
            windows.set_color_window.col_1["bg"]=Functions.rgb_to_hex(variables.color_max)
        if flags.flag_setting_color_min:
            variables.color_min = self.opened_for_using_image[x, y]
            flags.flag_setting_color_min = False
            print("Цвет позиции = {}".format(variables.color_min))
            windows.set_color_window.col_2["bg"]=Functions.rgb_to_hex(variables.color_min)
        print("Курсор находится на позиции х={} y={}".format(x, y))

    def refact_map(self):
        text_map_file = open(variables.path_to_text_map, "w")
        map_width, map_height = self.opened_img.size
        for y in range(map_height):
            for x in range(map_width):
                num_h = self.refact_pixel(self.opened_for_using_image[x, y])
                num_h = num_h // 1
                text_map_file.write((str)((int)(num_h)))
                if x < map_width-1:
                    text_map_file.write("\t")
            if y < map_height-1:
                text_map_file.write("\n")
        text_map_file.close()

    def refact_pixel(self, color_rgb=None, color_hsv=None):
        h = 0
        if color_hsv == None:
            color_hsv = Functions.rgb_to_hsv(color_rgb)
        if color_hsv[0]>180 and color_hsv[0]<300:
            h = self.find_height(color_hsv[1])
        else:
            h = 0
        return h

    def find_height(self, color_h):
        h = (color_h-variables.color_min_hsv[1])\
            /(variables.color_max_hsv[1]-variables.color_min_hsv[1])
        h = h * (variables.depth_max - variables.depth_min) + variables.depth_min
        return h

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
    root.resizable(False, False)

    root.mainloop()


