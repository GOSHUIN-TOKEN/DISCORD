from PIL import Image
from PIL import ImageDraw

for i in range(0, 201):
    black = Image.open("Layser_BaseBlack.png")
    green = Image.open("Layser_BaseGreen.png")
    if i == 0:
        pass
    else:
        green2 = green.resize((i, 10))
        black.paste(green2, (5,5))

    frame = Image.open("Layser_OverwrapFrame.png")

    ### aaa = Image.alpha_composite(black, green)
    black.save("aaa.png")
    layers = Image.alpha_composite(black, frame)
    layers.save("level_up_image_{0:03d}".format(i)+ ".png")