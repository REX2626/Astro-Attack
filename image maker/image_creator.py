from PIL import Image

#image = Image.open("image maker/Asteroid1.png")

"""image = image.convert("RGBA")
datas = image.getdata()

new_data = []
for item in datas:
    if item[0] < 1 and item[1] < 1 and item[2] < 1:
        new_data.append((255, 255, 255, 0))
    else:
        item = item[0], item[1], item[2], 255
        new_data.append(item)

image.putdata(new_data)
image.save("asteroid1.png")"""

im = Image.open("Asteroid1.png")
im2 = im.crop(im.getbbox())
im2.save("Asteroid_crop.png")