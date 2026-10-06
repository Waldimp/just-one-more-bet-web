"""Fuentes de la web, desde `assets/fonts/Geist_Pixel.zip` del juego.

- `geist-pixel.woff2`: Geist Pixel recortada a latin basico y latin-1 mas la puntuacion que usa
  el sitio, como instancia ESTATICA del eje ELSH=0 (pixel cuadrado). ~15 KB.
- `geist-pixel-bulbs.woff2`: la misma, instancia ELSH=20 (cada pixel es un circulo, como una
  bombilla) para los titulos de marquesina. ~15 KB.
  Por que estaticas y con los pixeles fundidos: cada glifo de Geist Pixel trae un contorno por
  pixel (cientos por letra) y el navegador los recorre al maquetar. Medido en Chrome con la CPU
  a 1/4: 12 s de layout con la fuente tal cual, 0,5 s sin ella. En la de pixel cuadrado las
  celdas se funden en un contorno por trazo (removeOverlaps, con skia-pathops); la de circulos
  no se puede fundir, pero solo la usan los titulos.
- `jomb-colon.woff2`: un solo glifo, el signo de colon (U+20A1), que Geist Pixel no trae. Se
  dibuja en su misma rejilla de 38 unidades: las celdas de su 'C' mas dos trazos inclinados.
  Es un derivado de Geist Pixel bajo OFL 1.1, con otro nombre de familia.
- `OFL.txt`: la licencia, que la OFL exige distribuir con la fuente.

Uso: python tools/build_fonts.py <ruta_juego>
"""
import io
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.removeOverlaps import removeOverlaps
from fontTools.varLib import instancer

OUT = Path(__file__).resolve().parent.parent / "assets" / "fonts"
VARIABLE = "GeistPixel-Regular-VariableFont_ELSH.ttf"
UNICODES = "U+0020-007E,U+00A0-00FF,U+2013-2014,U+2018-201E,U+2022,U+2026,U+2190-2193,U+20AC"
CELL = 38


def cells_of(font: TTFont, ch: str) -> set[tuple[int, int]]:
    glyf = font["glyf"]
    glyph = glyf[font.getBestCmap()[ord(ch)]]
    coords, ends, _ = glyph.getCoordinates(glyf)
    out, start = set(), 0
    for end in ends:
        pts = coords[start:end + 1]
        start = end + 1
        out.add((round(min(p[0] for p in pts) / CELL), round(min(p[1] for p in pts) / CELL)))
    return out


def colon_cells(font: TTFont) -> set[tuple[int, int]]:
    cells = set(cells_of(font, "C"))
    for base in (6, 10):
        for y in range(-2, 21):
            x = base + (y - 9) // 5  # inclinado: un paso cada 5 filas
            cells.update({(x, y), (x + 1, y)})
    return cells


def build_colon(static: TTFont, path: Path) -> None:
    pen = TTGlyphPen(None)
    for x, y in sorted(colon_cells(static)):
        x0, y0 = x * CELL, y * CELL
        pen.moveTo((x0, y0))
        pen.lineTo((x0, y0 + CELL))
        pen.lineTo((x0 + CELL, y0 + CELL))
        pen.lineTo((x0 + CELL, y0))
        pen.closePath()
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder([".notdef", "colonsign"])
    fb.setupCharacterMap({0x20A1: "colonsign"})
    fb.setupGlyf({".notdef": TTGlyphPen(None).glyph(), "colonsign": pen.glyph()})
    fb.setupHorizontalMetrics({".notdef": (500, 0), "colonsign": (684, 38)})
    fb.setupHorizontalHeader(ascent=1005, descent=-295)
    fb.setupNameTable({
        "familyName": "JOMB Colon",
        "styleName": "Regular",
        "copyright": "Glyph derived from Geist Pixel. Copyright 2026 The Geist Project Authors.",
        "licenseDescription": "SIL Open Font License, Version 1.1",
        "licenseInfoURL": "https://openfontlicense.org",
    })
    fb.setupOS2(sTypoAscender=1005, sTypoDescender=-295, usWinAscent=1005, usWinDescent=295)
    fb.setupPost()
    removeOverlaps(fb.font)
    fb.font.flavor = "woff2"
    fb.save(str(path))


def main() -> None:
    game = Path(sys.argv[1])
    OUT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(game / "assets/fonts/Geist_Pixel.zip") as zf, \
            tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / VARIABLE
        src.write_bytes(zf.read(VARIABLE))
        (OUT / "OFL.txt").write_bytes(zf.read("OFL.txt"))
        static = None
        for name, elsh in (("geist-pixel", 0), ("geist-pixel-bulbs", 20)):
            inst = instancer.instantiateVariableFont(TTFont(src), {"ELSH": elsh})
            if elsh == 0:
                # Las celdas se tocan: se funden en un solo contorno por trazo. De ~400 000
                # puntos a ~9 000, y la letra se ve igual. Es lo que hace barata la maquetacion.
                static = TTFont(src)
                static = instancer.instantiateVariableFont(static, {"ELSH": 0})
                removeOverlaps(inst)
            tmp_ttf = Path(tmp) / f"{name}.ttf"
            inst.save(str(tmp_ttf))
            subprocess.run([
                sys.executable, "-m", "fontTools.subset", str(tmp_ttf), f"--unicodes={UNICODES}",
                "--layout-features=kern,liga,calt", "--flavor=woff2",
                f"--output-file={OUT / (name + '.woff2')}",
            ], check=True)
        build_colon(static, OUT / "jomb-colon.woff2")
    for f in sorted(OUT.iterdir()):
        print(f"  {f.name}  {f.stat().st_size} B")


if __name__ == "__main__":
    main()
