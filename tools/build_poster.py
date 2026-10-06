"""Poster del trailer: un fotograma del propio video, devuelto a su pixel art nativo.

El trailer es pixel art a 640x360 escalado x3 (1920x1080). Se saca un fotograma con ffmpeg, se
reduce a 640x360 con la mediana de cada bloque de 3x3 (quita el ruido de la compresion H.264) y
se cuantiza sin tramado a 96 colores, que es la paleta real del plano. Sale en WebP sin perdida,
x2 (1280x720) y x1 (640x360), con escalado entero.

Por defecto, el segundo 16: el parqueo con el leon y el cartel, sin subtitulo. Ahi el trailer
en espanol y el ingles son identicos, asi que un solo poster vale para los dos.

Uso: python tools/build_poster.py <trailer.mp4> [segundo]
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "assets" / "img" / "shots"
SCALE = 3
NATIVE = (640, 360)


def main() -> None:
    video = Path(sys.argv[1])
    second = sys.argv[2] if len(sys.argv) > 2 else "16"
    with tempfile.TemporaryDirectory() as tmp:
        frame = Path(tmp) / "frame.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", second, "-i", str(video),
                        "-frames:v", "1", str(frame)], check=True)
        a = np.asarray(Image.open(frame).convert("RGB")).astype(int)
    w, h = NATIVE
    assert a.shape == (h * SCALE, w * SCALE, 3), f"esperaba {w * SCALE}x{h * SCALE}: {a.shape}"
    blocks = a.reshape(h, SCALE, w, SCALE, 3)
    native = Image.fromarray(np.median(blocks, axis=(1, 3)).astype(np.uint8), "RGB")
    native = native.quantize(colors=96, method=Image.Quantize.MEDIANCUT,
                             dither=Image.Dither.NONE).convert("RGB")
    native.resize((w * 2, h * 2), Image.NEAREST).save(
        OUT / "poster-trailer.webp", lossless=True, quality=100, method=6)
    native.save(OUT / "poster-trailer-1x.webp", lossless=True, quality=100, method=6)
    print("ok", OUT / "poster-trailer.webp")


if __name__ == "__main__":
    main()
