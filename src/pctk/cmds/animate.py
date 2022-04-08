import os, sys
import glob
from PIL import Image
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM



output_dir = sys.argv[1]

# Create the frames

patterns = os.path.join(output_dir, "*.svg")
globbing = sorted(glob.glob(patterns))

frames = []
for i in globbing:
    print("Processin image %s" % i)
    drawing = svg2rlg(i)
    new_frame = renderPM.drawToPIL(drawing, dpi=200)
    frames.append(new_frame)

# Save into a GIF file that loops forever
frames[0].save('animation.gif', format='GIF', 
                append_images=frames[1:],
                save_all=True,
                duration=150, loop=0, quality=200)