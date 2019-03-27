from PIL import Image

# Dunno
highestPoint = 11000

# TxT files
name_of_txt_file_with_heights = "HeightMap.txt"
name_of_txt_file_with_danger_of_heights = "DepthDangerZone.txt"

# Images (Program won't work with formats, that don't support RGBA format)
name_of_map_image = "Map.png"
name_of_depth_danger_image = "DangerDepthMask.png"
name_of_the_final_image = "Finale.png"

# Map colours
ground_colour = 160, 82, 45, 255

# Colours of zones
safe_zone_colour = 255, 255, 255, 0  # Transparent white
middle_danger_zone_colour = 255, 255, 0, 150  # Half-transparent yellow
full_danger_zone_colour = 255, 0, 0, 150  # Half-transparent red


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
    if danger_meter <= 0.25:  # Check if safe zone
        return safe_zone_colour
    elif danger_meter < 0.75:  # Check if middle-danger zone
        return middle_danger_zone_colour
    else:  # Danger zone!
        return full_danger_zone_colour


def list_nums(txt_name):
    read = open(txt_name, "r")
    content = read.readlines()  # List of strings with depth numbers
    read.close()
    return content


def draw_map(num_list, img_name):

    im = Image.new('RGBA', (len(num_list[0].split()), len(num_list)))  # Create empty matrix-sized image
    x = 0  # Python index system is... questionable,
    y = 0  # so there is a workaround
    for i in num_list:
        for j in i.split():
            im.putpixel((x, y), map_colouring(int(j)))  # Colouring corresponding pixels
            x += 1
        x = 0  # Go back at the end of each line
        y += 1  # Next line
    im.save(img_name)  # or any image format
    im.close()


def draw_danger(num_list, img_name):
    im = Image.new('RGBA', (len(num_list[0].split()), len(num_list)))  # Create empty matrix-sized image
    x = 0  # Python index system is... questionable,
    y = 0  # so there is a workaround
    for i in num_list:
        for j in i.split():
            im.putpixel((x, y), danger_colouring(float(j)))  # Colouring corresponding pixels
            x += 1
        x = 0  # Go back at the end of each line
        y += 1  # Next line
    im.save(img_name)  # or any image format
    im.close()


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
        finale.save(name_of_the_final_image)  # Save image and close all
        finale.close()
    image1.close()
    image2.close()


def main():
    # Read file
    matrix_map = list_nums(name_of_txt_file_with_heights)
    # Draw matrix
    draw_map(matrix_map, name_of_map_image)
    danger_map = list_nums(name_of_txt_file_with_danger_of_heights)
    draw_danger(danger_map, name_of_depth_danger_image)
    combine(name_of_map_image, name_of_depth_danger_image)


if __name__ == '__main__':
    main()
