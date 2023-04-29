import sys
from PIL import Image

# define the ASCII characters to use for the image
ASCII_CHARS = ["#", "S", "%", "?", "*", "+", ";", ",", "."]

# get the path to the image from the command line arguments
try:
    image_path = sys.argv[1]
except IndexError:
    print("Please provide the path to the image as an argument.")
    sys.exit()

# open the image file
try:
    with Image.open(image_path) as image:
        # convert the image to grayscale
        grayscale_image = image.convert("L")

        # resize the image to a smaller size
        width, height = grayscale_image.size
        aspect_ratio = height/width
        new_width = 100
        new_height = int(aspect_ratio * new_width)
        grayscale_image = grayscale_image.resize((new_width, new_height))

        # generate the ASCII representation of the image
        ascii_image = ""
        for pixel_value in grayscale_image.getdata():
            index = int(pixel_value / 255 * (len(ASCII_CHARS) - 1))
            ascii_image += ASCII_CHARS[index]

        # print the ASCII image to the console
        for row in range(0, len(ascii_image), new_width):
            print(ascii_image[row:row + new_width])
except Exception as e:
    print("An error occurred while processing the image: ", e)
    sys.exit()
