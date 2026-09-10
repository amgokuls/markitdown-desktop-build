from PIL import Image
from pathlib import Path

icon_path = Path("resources/icons/AppIcon.jpg")
if icon_path.exists():
    img = Image.open(icon_path)
    img.save("resources/icons/AppIcon.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
    print("Created AppIcon.ico")
