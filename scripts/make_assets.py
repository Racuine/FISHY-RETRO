from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1]; assets=root/'assets';assets.mkdir(exist_ok=True)
S=96
im=Image.new('RGB',(S,S),'#48b9e0');d=ImageDraw.Draw(im)
def r(x0,y0,x1,y1,c):d.rectangle((x0,y0,x1,y1),fill=c)
# Light shafts and ocean bubbles
for i in range(4):r(8+i*26,0,12+i*26,18,'#85d9f0')
for x,y in [(15,33),(22,22),(78,27),(84,66),(17,75)]:
 d.rectangle((x,y,x+4,y+4),outline='#d6faff',width=1)
# Coral/seaweed accents
for x in (9,78):
 r(x,74,x+6,95,'#238b6d');r(x-3,82,x+8,86,'#2a9e79')
# fish silhouette with pixelated tail and fins
r(15,42,30,51,'#ec8b44');r(15,52,30,61,'#ec8b44')
r(26,35,72,66,'#f4a63f');r(30,39,76,62,'#ffcd63');r(39,30,54,38,'#ee9940');r(42,63,57,70,'#ee9940')
r(65,44,72,51,'#173a52');r(67,44,69,46,'#ffffff');r(72,55,78,57,'#e78a51')
icon=im.resize((1024,1024),Image.Resampling.NEAREST)
icon.save(assets/'icon-1024.png')
# Square splash graphic, intentionally smaller than screen: Android 12 crops launch icons.
splash=Image.new('RGBA',(432,432),(0,0,0,0));mini=im.resize((216,216),Image.Resampling.NEAREST);splash.paste(mini,(108,108));splash.save(assets/'splash.png')
for dpi,size in [('mdpi',48),('hdpi',72),('xhdpi',96),('xxhdpi',144),('xxxhdpi',192)]:
 dest=assets/dpi;dest.mkdir(exist_ok=True)
 im.resize((size,size),Image.Resampling.NEAREST).save(dest/'ic_launcher.png')
 im.resize((size,size),Image.Resampling.NEAREST).save(dest/'ic_launcher_round.png')
 # foreground is enlarged transparent image to leave margin for Android adaptive mask
 fore=Image.new('RGBA',(size*2,size*2),(0,0,0,0))
 scaled=im.resize((size,size),Image.Resampling.NEAREST)
 fore.paste(scaled,(size//2,size//2));fore.save(dest/'ic_launcher_foreground.png')
print('Created icon-1024.png, splash.png and density-specific launcher icons')
