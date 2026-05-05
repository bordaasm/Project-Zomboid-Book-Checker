from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
ICON_SOURCE = ROOT / "Src" / "img" / "Carpentry.png"
ICON_TARGET = ROOT / "assets" / "app.ico"


def main() -> None:
    ICON_TARGET.parent.mkdir(parents=True, exist_ok=True)
    image = Image.open(ICON_SOURCE).convert("RGBA")
    image.save(ICON_TARGET, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])


if __name__ == "__main__":
    main()
