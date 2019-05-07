from PIL import Image

# map sizes
width_of_map = 0
height_of_map = 0

# Dunno
highestPoint = 10
lowestPoint = 10

# Input txt files (they must have same height and width)
txt_file_with_heights = "G:\Maps\Single_map.txt"
txt_file_with_danger_of_heights = "DepthDangerZone.txt"

# Output images (Program won't work with formats, that don't support RGBA format)
map_image = "Map.png"
depth_danger_image = "DangerDepthMask.png"
final_image = "Finale.png"

# Map colours
ground_colour = 160, 82, 45, 255
path_colour = 255, 255, 255, 255

# Colours of zones
safe_zone_colour = 255, 255, 255, 0  # Transparent white
low__danger_zone_colour = 255, 255, 204, 255  # Half-transparent light yellow
middle_danger_zone_colour = 255, 255, 0, 255  # Half-transparent yellow
high_danger_zone_colour = 255, 140, 0, 255  # Half-transparent orange
full_danger_zone_colour = 255, 0, 0, 255  # Half-transparent red

draft_max = 2
draft_min = 1

zones = {
        0: safe_zone_colour,
        0.25: low__danger_zone_colour,
        0.5: middle_danger_zone_colour,
        0.75: high_danger_zone_colour,
        1: full_danger_zone_colour
        }


def createImageFile(name, width, height):
    im = Image.new('RGBA', (width, height))
    for y in range(height):
        for x in range(width):
            im.putpixel((x,y), (50,50,255,255))
    im.save(name)
    im.close()

def draw_list_of_lines(list_of_lines, image=final_image):
    im = Image.open(image)
    for line in list_of_lines:
        draw_line(line[0], line[1], line[2], line[3], im)
    im.save(image)
    im.close()

def draw_line(x_st, y_st, x_en, y_en, im):
    if x_st == x_en:
        if y_st >= y_en:
            start = y_en
            end = y_st
        else:
            start = y_st
            end = y_en
        for y in range(start, end+1):
            if 0 <= x_st < width_of_map and 0 <= y < height_of_map:
                im.putpixel((x_st, y), path_colour)
    else:
        k = (y_en - y_st)/(x_en - x_st)
        b = y_en - x_en*k
        if x_st >= x_en:
            start = x_en
            end = x_st
            y_pr = y_en
        else:
            start = x_st
            end = x_en
            y_pr = y_st
        for x in range(start, end):
            y = int(k*x + b)
            if y>y_pr:
                for yy in range(y_pr, y+1):
                    if 0 <= x < width_of_map and 0 <= yy < height_of_map:
                        im.putpixel((x, yy), path_colour)
            else:
                for yy in range(y, y_pr+1):
                    if 0 <= x < width_of_map and 0 <= yy < height_of_map:
                        im.putpixel((x, yy), path_colour)
            y_pr = y

def draw_list_of_circles(list_of_circles, image=final_image):
    im = Image.open(image)
    for circle in list_of_circles:
        draw_circle(circle[0], circle[1], circle[2], im)
    im.save(image)
    im.close()

def draw_circle(center_x, center_y, radius, im):
    # width, height = im.size  # Get size of image
    right = center_x + radius  # Define part of circumscribed square which is in the image
    left = center_x - radius
    top = center_y - radius
    bot = center_y + radius
    temp = radius*radius
    if right >= width_of_map:
        right = width_of_map - 1
    if left < 0:
        left = 0
    if top < 0:
        top = 0
    if bot >= height_of_map:
        bot = height_of_map - 1
    for y in range(top, bot+1, 1):  # Run through all pixels of this part and find all of them with coordinates
        for x in range(left, right+1, 1):  # suitable for this circle
            if ((y - center_y)*(y - center_y) + (x - center_x)*(x - center_x)) - temp <= 0:
                im.putpixel((x, y), full_danger_zone_colour)


def map_colouring(depth):
    if depth == 0:
        return ground_colour
    else:
        temp = int(depth / highestPoint * 255)
        r = 0
        g = 255 - temp
        b = 255 - temp
        return r, g, b, 255

def danger_colouring(danger_meter):
    return zones.get(danger_meter)  # Get a zone colour from dict

def list_nums(txt_name):
    read = open(txt_name, "r")
    content = read.readlines()  # List of strings with depth numbers
    read.close()
    return content

def classify_warning(depth):
    temp = (draft_max - depth) / (draft_max - draft_min)
    if temp <= 0:
        return '0'
    if temp <= 0.25:
        return '0.25'
    if temp <= 0.50:
        return '0.5'
    if temp <= 0.75:
        return '0.75'
    else:
        return '1'


def draw_map(num_list):
    global highestPoint, lowestPoint
    main_im = Image.new('RGBA', (width_of_map, height_of_map))  # Create empty matrix-sized image twice
    danger_im = Image.new('RGBA', (width_of_map, height_of_map))
    txt_file = open(txt_file_with_danger_of_heights, 'w+')  # Create/open txt file for dangers
    x = 0  # Python index system is... quite cumbersome,
    y = 0  # so there is a workaround
    highestPoint = int((num_list[0].split('\t'))[0])
    lowestPoint = int((num_list[0].split('\t'))[0])
    for i in num_list:
        for j in i.split('\t'):
            intj = int(j)
            if intj > highestPoint:
                highestPoint = intj
            if intj < lowestPoint:
                lowestPoint = intj
            depth_warning = classify_warning(intj)  # Classify depth
            txt_file.write(depth_warning)  # Write into txt file for dangers
            if x < width_of_map - 1:
                txt_file.write('\t')  # Write into txt file for dangers
            main_im.putpixel((x, y), map_colouring(intj))  # Colouring corresponding pixels
            danger_im.putpixel((x, y), danger_colouring(float(depth_warning)))  # RFD: draw dangers
            x += 1
        if y < height_of_map - 1:
            txt_file.write('\n')  # Write into txt file for dangers
        x = 0  # Go back at the end of each line
        y += 1  # Next line
    highestPoint = highestPoint * 2
    main_im.save(map_image)  # Save images and close all files
    danger_im.save(depth_danger_image)
    main_im.close()
    danger_im.close()
    txt_file.close()

def combine(image1_n, image2_n):
    image1 = Image.open(image1_n)  # Open both images
    image2 = Image.open(image2_n)
    width1, height1 = image1.size  # Get resolutions of images
    width2, height2 = image2.size
    if width1 == width2 and height1 == height2:  # Check if same resolution
        finale = Image.new('RGBA', (width1, height1))  # Create image for filling
        for y in range(height1):
            for x in range(width1):
                r1, g1, b1, a1 = image1.getpixel((x, y))  # Get pixel values
                r2, g2, b2, a2 = image2.getpixel((x, y))
                if a2 == 0:     # Check if safe zone and fill pixel
                    finale.putpixel((x, y), (r1, g1, b1, a1))
                else:
                    finale.putpixel((x, y), (r2, g2, b2, a2))
        finale.save(final_image)  # Save image and close all
        finale.close()
    image1.close()
    image2.close()


def full_map_conjunction():
    global height_of_map, width_of_map
    # Read file
    matrix_map = list_nums(txt_file_with_heights)
    height_of_map = len(matrix_map)
    width_of_map = len(matrix_map[0].split('\t'))
    # Draw 2 main images
    draw_map(matrix_map)
    # Draw final image
    combine(map_image, depth_danger_image)

def set_parameters(txt_file="", draft__min=0, draft__max=0, width=0, height=0):
    global txt_file_with_heights, draft_min, draft_max, width_of_map, height_of_map
    txt_file_with_heights = txt_file
    draft_min, draft_max = draft__min, draft__max
    width_of_map, height_of_map = width, height

def get_map_sizes():
    return width_of_map, height_of_map

if __name__ == '__main__':
    full_map_conjunction()
