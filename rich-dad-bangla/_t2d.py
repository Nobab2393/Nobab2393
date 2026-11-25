from PIL import Image
import cast2d as c
S=2
img = Image.new("RGB",(1920*S,1080*S), c.CREAM)
p = c.Pen(img, S)
p.rrect([0,760,1920,1080], 0, c.HILL, 0, oc=(0,0,0))
c.house(p, 300, 760, 300, 210)
c.house(p, 1560, 780, 260, 190, wall=c.WALL_D, roof=c.ROOF_D)
c.lamp(p, 120, 780, 380)
c.bench(p, 760, 900, 420)
c.rabbit(p, 560, 900, 1.05)
c.eagle(p, 900, 900, 0.95, wings=0.0)
c.fox(p, 1200, 900, 0.95)
c.turtle(p, 1520, 900, 0.95)
img.resize((1920,1080), Image.LANCZOS).save("/tmp/cast.png")
print("ok")
