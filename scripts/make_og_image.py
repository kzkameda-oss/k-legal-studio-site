"""SNS・LINE 共有用の画像（og:image）を作る。事務所名や文言を変えたときだけ流し直す。

    python scripts/make_og_image.py

出力：public/og.png（1200×630）。Base.astro の og:image / twitter:image が参照する。
配色はサイトと同じ（紺 #1b2a41・金 #b8893a）。写真が用意できたら差し替えてよい。
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "public" / "og.png"
W, H = 1200, 630
NAVY, NAVY_DEEP = (27, 42, 65), (18, 32, 58)
GOLD, GOLD_LIGHT, WHITE = (184, 137, 58), (231, 211, 173), (255, 255, 255)

SERIF = ["C:/Windows/Fonts/yumindb.ttf", "C:/Windows/Fonts/NotoSerifJP-VF.ttf", "C:/Windows/Fonts/msmincho.ttc"]
SANS = ["C:/Windows/Fonts/YuGothB.ttc", "C:/Windows/Fonts/NotoSansJP-VF.ttf", "C:/Windows/Fonts/meiryob.ttc"]


def font(cands: list[str], size: int) -> ImageFont.FreeTypeFont:
    for p in cands:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    raise SystemExit("日本語フォントが見つからない")


def main() -> None:
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    # 背景：下に向かって少し濃く、右上に薄い円（サイトのヒーローと同じ意匠）
    for y in range(H):
        t = y / H
        c = tuple(round(NAVY[i] + (NAVY_DEEP[i] - NAVY[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse([760, -260, 1420, 400], outline=(231, 211, 173, 38), width=46)
    img.paste(ring, (0, 0), ring)
    d = ImageDraw.Draw(img)

    # 上下の金の帯
    d.rectangle([0, 0, W, 10], fill=GOLD)
    d.rectangle([0, H - 10, W, H], fill=GOLD)

    # ロゴ（角丸の四角に「亀」）
    x0, y0, s = 90, 96, 104
    d.rounded_rectangle([x0, y0, x0 + s, y0 + s], radius=18, fill=NAVY_DEEP, outline=GOLD, width=3)
    f_logo = font(SERIF, 66)
    bb = d.textbbox((0, 0), "亀", font=f_logo)
    d.text((x0 + (s - (bb[2] - bb[0])) / 2 - bb[0], y0 + (s - (bb[3] - bb[1])) / 2 - bb[1]), "亀", font=f_logo, fill=(201, 161, 90))

    # 小見出し
    d.text((x0 + s + 28, y0 + 14), "奈良市西大寺の行政書士事務所", font=font(SANS, 30), fill=GOLD_LIGHT)
    d.text((x0 + s + 28, y0 + 62), "Kameda Legal Studio", font=font(SANS, 24), fill=GOLD)

    # 事務所名
    d.text((90, 252), "亀田行政書士事務所", font=font(SERIF, 96), fill=WHITE)

    # 金の罫線
    d.rectangle([92, 380, 92 + 120, 384], fill=GOLD)

    # 取扱業務
    d.text((90, 412), "建設業許可・経営事項審査・農地転用", font=font(SANS, 38), fill=WHITE)
    d.text((90, 466), "産業廃棄物収集運搬業許可・宅建業免許", font=font(SANS, 38), fill=WHITE)

    # URL
    f_url = font(SANS, 28)
    url = "k-legal-studio.com"
    bb = d.textbbox((0, 0), url, font=f_url)
    d.text((W - 90 - (bb[2] - bb[0]), H - 78), url, font=f_url, fill=GOLD_LIGHT)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"saved {OUT.relative_to(REPO)} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
