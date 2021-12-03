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
    lineheight = 15

    # Load font to display
    font = ImageFont.truetype(font="/home/pi/EasyKeyCabinet/src/PressStart2P.ttf", size=12)

    # Write three lines of text.
    draw.text((padding, top),    l1,  font=font, fill=255)
    draw.text((padding, top + lineheight), l2, font=font, fill=255)
    draw.text((padding, top + 2 * lineheight), l3, font=font, fill=255)
    draw.text((padding, top + 3 * lineheight), l4, font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.show()
    
    
def wltd(strings):
    write_to_display(strings[0], strings[1], strings[2], strings[3])
