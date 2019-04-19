from PIL import Image

highestPoint=0
lowestPoint = 0
txt_file_with_heights="0"
txt_file_with_danger_of_heights="0"
map_image="0"
depth_danger_image="0"
final_image="0"
ground_colour=0
path_colour=0
zones=0

def main(filename):
    global highestPoint,lowestPoint,txt_file_with_heights,txt_file_with_danger_of_heights,map_image,depth_danger_image,final_image,ground_colour,path_colour,zones
    # Dunno
    highestPoint = 25
    lowestPoint = 0

    # Input txt files (they must have same height and width)
    txt_file_with_heights = filename
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
    low__danger_zone_colour = 255, 255, 204, 150  # Half-transparent light yellow
    middle_danger_zone_colour = 255, 255, 0, 150  # Half-transparent yellow
    high_danger_zone_colour = 255, 140, 0, 150  # Half-transparent orange
    full_danger_zone_colour = 255, 0, 0, 150  # Half-transparent red

    zones = {
        0: safe_zone_colour,
        0.25: low__danger_zone_colour,
        0.5: middle_danger_zone_colour,
        0.75: high_danger_zone_colour,
        1: full_danger_zone_colour
    }


def draw_line(x_st, y_st, x_en, y_en):
    global map_image, path_colour
    im = Image.open(map_image)
    if x_st == x_en:
        if y_st >= y_en:
            start = y_en
            end = y_st
        else:
            start = y_st
            end = y_en
        for y in range(start, end + 1):
            im.putpixel((x_st, y), path_colour)
    else:
        k = (y_en - y_st) / (x_en - x_st)
        b = y_en - x_en * k
        if x_st >= x_en:
            start = x_en
            end = x_st
            y_pr = y_en
        else:
            start = x_st
            end = x_en
            y_pr = y_st
        for x in range(start, end):
            y = int(k * x + b)
            if y > y_pr:
                for yy in range(y_pr, y + 1):
                    im.putpixel((x, yy), path_colour)
            else:
                for yy in range(y, y_pr + 1):
                    im.putpixel((x, yy), path_colour)
            y_pr = y
    im.save(map_image)
    im.close()

def circle_draw(center_x, center_y, radius):
    global map_image, ground_colour
    im = Image.open(map_image)  # Open image
    width, height = im.size  # Get size of image
    right = center_x + radius  # Define part of circumscribed square which is in the image
    left = center_x - radius
    top = center_y - radius
    bot = center_y + radius
    temp = radius * radius
    while right >= width:
        right -= 1
    while left < 0:
        left += 1
    while top < 0:
        top += 1
    while bot >= height:
        bot -= 1
    for y in range(top, bot + 1, 1):  # Run through all pixels of this part and find all of them with coordinates
        for x in range(left, right + 1, 1):  # suitable for this circle
            if ((y - center_y) * (y - center_y) + (x - center_x) * (x - center_x)) - temp <= 0:
                im.putpixel((x, y), ground_colour)
    im.save(map_image)
    im.close()

def map_colouring(depth):
    global highestPoint, ground_colour
    if depth == 0:
        return ground_colour
    else:
        temp = int(depth / highestPoint * 255)
        r = 0
        g = 255 - temp
        b = 255 - temp
        return r, g, b, 255

def danger_colouring(danger_meter):
    global zones
    return zones.get(danger_meter)  # Get a zone colour from dict

def list_nums(txt_name):
    read = open(txt_name, "r")
    content = read.readlines()  # List of strings with depth numbers
    read.close()
    return content

def classify_warning(depth):
    global highestPoint, lowestPoint
    temp = (highestPoint - depth) / (highestPoint - lowestPoint)
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
    global txt_file_with_danger_of_heights, map_image, depth_danger_image
    main_im = Image.new('RGBA', (len(num_list[0].split()), len(num_list)))  # Create empty matrix-sized image twice
    danger_im = Image.new('RGBA', (len(num_list[0].split()), len(num_list)))
    txt_file = open(txt_file_with_danger_of_heights, 'w+')  # Create/open txt file for dangers
    x = 0  # Python index system is... quite cumbersome,
    y = 0  # so there is a workaround
    for i in num_list:
        for j in i.split():
            depth_warning = classify_warning(int(j))  # Classify depth
            txt_file.write(depth_warning + '\t')  # Write into txt file for dangers
            main_im.putpixel((x, y), map_colouring(int(j)))  # Colouring corresponding pixels
            danger_im.putpixel((x, y), danger_colouring(float(depth_warning)))  # RFD: draw dangers
            x += 1
        x = 0  # Go back at the end of each line
        y += 1  # Next line
    main_im.save(map_image)  # Save images and close all files
    danger_im.save(depth_danger_image)
    main_im.close()
    danger_im.close()
    txt_file.close()

def combine(image1_n, image2_n):
    global final_image
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
                if a2 == 0:  # Check if safe zone and fill pixel
                    finale.putpixel((x, y), (r1, g1, b1, a1))
                else:
                    finale.putpixel((x, y), (r2, g2, b2, a2))
        finale.save(final_image)  # Save image and close all
        finale.close()
    image1.close()
    image2.close()

def full_map_conjunction(filename):
    global txt_file_with_heights, txt_file_with_danger_of_heights, map_image, depth_danger_image, final_image
    main(filename)
    # Read file
    matrix_map = list_nums(txt_file_with_heights)
    draw_map(matrix_map)
    # danger_matrix = list_nums(txt_file_with_danger_of_heights)
    # draw_danger(danger_matrix, depth_danger_image)
    combine(map_image, depth_danger_image)
    # circle_draw(780, 500, 50, final_image)
    # draw_line(100, 300, 500, 400, final_image)
    print(highestPoint, lowestPoint, txt_file_with_heights, txt_file_with_danger_of_heights, map_image, depth_danger_image, final_image, ground_colour, path_colour,zones)

