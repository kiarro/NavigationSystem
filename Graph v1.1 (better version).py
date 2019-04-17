from PIL import Image


# Dunno
highestPoint = 2000
lowestPoint = 100

# Input txt files (they must have same height and width)
txt_file_with_heights = "Map9_text_100_1500.txt"
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

vanyas_max_constant = 500
vanyas_min_constant = 100

zones = {
        0: safe_zone_colour,
        0.25: low__danger_zone_colour,
        0.5: middle_danger_zone_colour,
        0.75: high_danger_zone_colour,
        1: full_danger_zone_colour
        }


def draw_line(x_start, y_start, x_end, y_end, image):
    im = Image.open(image)
    if x_start == x_end:   # If x axis are the same y = kx + b does not work, so line turns into x = constant
        if y_start >= y_end:
            start = y_end
            end = y_start
        else:
            start = y_start
            end = y_end
        for y in range(start, end+1):
            im.putpixel((x_start, y), path_colour)
    else:  # Calculating y = kx + b
        k = (y_end - y_start)/(x_end - x_start)
        b = y_end - x_end*k
        if x_start >= x_end:
            start = x_end
            end = x_start
        else:
            start = x_start
            end = x_end
        for x in range(start, end+1):
            y = int(k*x + b)
            im.putpixel((x, y), path_colour)
    im.save(image)
    im.close()


def draw_circle(center_x, center_y, radius, image):
    im = Image.open(image)  # Open image
    width, height = im.size  # Get size of image
    right = center_x + radius  # Define part of circumscribed square which is in the image
    left = center_x - radius
    top = center_y - radius
    bot = center_y + radius
    temp = radius*radius
    while right >= width:
        right -= 1
    while left < 0:
        left += 1
    while top < 0:
        top += 1
    while bot >= height:
        bot -= 1
    for y in range(top, bot+1, 1):  # Run through all pixels of this part and find all of them with coordinates
        for x in range(left, right+1, 1):  # suitable for this circle
            if ((y - center_y)*(y - center_y) + (x - center_x)*(x - center_x)) - temp <= 0:
                im.putpixel((x, y), ground_colour)
    im.save(image)
    im.close()


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
    temp = (vanyas_max_constant - depth) / (vanyas_max_constant - vanyas_min_constant)
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
    # Read file
    matrix_map = list_nums(txt_file_with_heights)
    # Draw 2 main images
    draw_map(matrix_map)
    # Draw final image
    combine(map_image, depth_danger_image)


if __name__ == '__main__':
    full_map_conjunction()
