from PIL import Image, ImageTk
import time

background = Image.open('img/televo/Glide1.webp')
foreground = Image.open("recusant_sigil.png").resize(background.size)

final_image = Image.alpha_composite(background, foreground)
time.sleep(10)
ImageTk.PhotoImage(final_image)

# background = Image.alpha_composite(
#     Image.new("RGBA", background.size),
#     background.convert('RGBA')
# )

# background.paste(
#     foreground,
#     (x, y),
#     foreground
# )

# background.show()