import time

from board import SCL, SDA
import busio

import adafruit_ssd1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Create the I2C interface
i2c = busio.I2C(SCL, SDA)

# 128x64 display with hardware I2C:
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

def clear_display():
    """ Clears the OLED-screen """
    disp.fill(0)
    disp.show()


def write_to_display(l1, l2, l3, l4):
    """
    Writes the lines to the OLED-screen'.
    lines over 10 characters will not have enough space.
    """
    clear_display()

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    # First define some constants to allow easy resizing of shapes.
    padding = 2
    top = 0

    # Load font to display
    font = ImageFont.truetype(font="PressStart2P.ttf", size=12)

    x = padding

    # Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
    # Some other nice fonts to try: http://www.dafont.com/bitmap.php
    #font = ImageFont.truetype('Minecraftia.ttf', 8)

    # Write three lines of text.
    draw.text((x, top),    l1,  font=font, fill=255)
    draw.text((x, top+15), l2, font=font, fill=255)
    draw.text((x, top+30), l3, font=font, fill=255)
    draw.text((x, top+45), l4, font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.show()

write_to_display("Test", "genom att", "trycka på", "en av dem")
