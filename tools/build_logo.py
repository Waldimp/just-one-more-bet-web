"""Logo, favicon e iconos de app desde el logo del juego (`assets/icons/branding/`).

Fuente: `logo_animation.png`, rejilla 3x3 de celdas de 64x64 con la ficha girando en 8 cuadros
(la novena celda va vacia). Su primer cuadro es `logo_final.png` pixel a pixel. Se usa esta y no
`logo_animation_grid_2x4.png` porque la 2x4 tiene la ficha 2 px corrida: el giro no empezaria ni
acabaria en el logo quieto.

Salidas:
  assets/img/logo/logo-64.png      el logo quieto, 64x64 (cabecera x1, pie x2)
  assets/img/logo/logo-spin.png    tira de 512x64 con los 8 cuadros del giro (cabecera)
  assets/img/icons/favicon-64.png  favicon grande (lo usan las pestanas de pantallas densas)
  assets/img/icons/favicon-32.png  y favicon.ico (16, 32, 48): reducidos por promedio, porque a
                                   esos tamanos la letra de la ficha no se puede conservar
  assets/img/icons/apple-touch-icon.png  180x180: logo x2 sobre fondo opaco (iOS lo exige)
  assets/img/icons/icon-192.png, icon-512.png  logo x3 y x8, escala entera exacta

Uso: python tools/build_logo.py <ruta_juego>
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CELL = 64
FRAMES = 8
WINE_0 = (36, 6, 10, 255)  # c224 de la paleta maestra


def main() -> None:
    game = Path(sys.argv[1])
    branding = game / "assets/icons/branding"
    logo = Image.open(branding / "logo_final.png").convert("RGBA")
    sheet = Image.open(branding / "logo_animation.png").convert("RGBA")
    frames = [sheet.crop(((i % 3) * CELL, (i // 3) * CELL, (i % 3 + 1) * CELL, (i // 3 + 1) * CELL))
              for i in range(FRAMES)]
    assert frames[0].tobytes() == logo.tobytes(), "el primer cuadro del giro no es el logo quieto"

    out_logo = ROOT / "assets/img/logo"
    out_icons = ROOT / "assets/img/icons"
    out_logo.mkdir(parents=True, exist_ok=True)
    out_icons.mkdir(parents=True, exist_ok=True)

    logo.save(out_logo / "logo-64.png", optimize=True)
    strip = Image.new("RGBA", (CELL * FRAMES, CELL), (0, 0, 0, 0))
    for i, frame in enumerate(frames):
        strip.alpha_composite(frame, (i * CELL, 0))
    strip.save(out_logo / "logo-spin.png", optimize=True)

    logo.save(out_icons / "favicon-64.png", optimize=True)
    logo.resize((32, 32), Image.BOX).save(out_icons / "favicon-32.png", optimize=True)
    logo.save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    apple = Image.new("RGBA", (180, 180), WINE_0)
    apple.alpha_composite(logo.resize((128, 128), Image.NEAREST), (26, 26))
    apple.convert("RGB").save(out_icons / "apple-touch-icon.png", optimize=True)
    logo.resize((192, 192), Image.NEAREST).save(out_icons / "icon-192.png", optimize=True)
    logo.resize((512, 512), Image.NEAREST).save(out_icons / "icon-512.png", optimize=True)

    for f in sorted([*out_logo.iterdir(), *out_icons.iterdir(), ROOT / "favicon.ico"]):
        print(f"  {f.relative_to(ROOT)}  {f.stat().st_size} B")


if __name__ == "__main__":
    main()
