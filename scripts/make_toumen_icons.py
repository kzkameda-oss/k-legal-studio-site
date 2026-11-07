"""登録免許税クイック計算機（PWA）のアイコンを作る。1回だけ流せばよい。

    python scripts/make_toumen_icons.py

出力：public/tools/<隠しパス>/icon-192.png / icon-512.png / icon-180.png
青地（#4A7FC5、計算機のアクセント色）に白で「税」。maskable 用に余白をとった全面塗り。
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
DEST = REPO / "public" / "tools" / "vzpqflysskptq1"
FONT_CANDIDATES = [
    "C:/Windows/Fonts/YuGothB.ttc",
    "C:/Windows/Fonts/meiryob.ttc",
    "C:/Windows/Fonts/NotoSansJP-VF.ttf",
    "C:/Windows/Fonts/msgothic.ttc",
]
BG = (74, 127, 197)
FG = (255, 255, 255)


def pick_font(size: int) -> ImageFont.FreeTypeFont:
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    raise SystemExit("日本語フォントが見つからない")


def render(size: int) -> Image.Image:
    img = Image.new("RGB", (size, size), BG)
    d = ImageDraw.Draw(img)
    font = pick_font(int(size * 0.56))
    text = "税"
    bbox = d.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size - w) / 2 - bbox[0]
    y = (size - h) / 2 - bbox[1]
    d.text((x, y), text, font=font, fill=FG)
    return img


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    for s in (192, 512, 180):
        out = DEST / f"icon-{s}.png"
        render(s).save(out, optimize=True)
        print("wrote", out)


if __name__ == "__main__":
    main()
