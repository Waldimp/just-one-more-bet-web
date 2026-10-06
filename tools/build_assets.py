"""Imagenes de la web a partir de capturas reales del juego y de su arte propio.

Entradas:
  <capturas>  carpeta con los PNG que sacan los scripts de `tools/godot/` (640x360 nativos)
  <juego>     raiz del repo del juego (solo se lee)

Salidas (en `assets/img/`):
  shots/*.webp     capturas x2 vecino mas cercano (1280x720), WebP sin perdida
  map/casino.webp  plano entero del casino de la semilla 777, a resolucion nativa
  pins/pins.png    los 32 pines del juego (arte propio, 16x16) en una hoja de 8x4
  ui/coin.png      la moneda de la lluvia de victoria (arte propio, 4 cuadros)
  ui/carpet.png    baldosa de alfombra dibujada para la web con la paleta maestra
  icons/*          favicon en SVG, PNG e ICO
  og/og-es.png, og-en.png  1200x630 para redes, montadas sobre el hero nocturno

Uso: python tools/build_assets.py <capturas> <juego>
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"

# nombre en la web -> archivo de captura
SHOTS = {
    "historia-1": "clean_intro_0_03.6.png",
    "historia-2": "clean_intro_1_08.6.png",
    "historia-3": "clean_intro_2_05.8.png",
    "historia-4": "clean_intro_3_05.2.png",
    "dia-salon": "s777_room_lounge.png",
    "mesa-tragamonedas": "act_slots_05.png",
    "mesa-ruleta": "act_rl_spin_03.png",
    "mesa-blackjack": "act_bj_hit_03.png",
    "mesa-caballos": "act_hr_race_05.png",
    "brujo": "s777_closeup_brujo.png",
    "barra": "s777_closeup_bar.png",
    "cobrador": "s777_collector.png",
    "sala-tragamonedas": "s777_room_slots_room.png",
    "sala-ruleta": "s777_room_roulette_room.png",
    "sala-blackjack": "s777_room_blackjack_room.png",
    "sala-caballos": "s777_room_horse_room.png",
    "sala-bar": "s777_room_bar_room.png",
    "sala-brujo": "s777_room_brujo_room.png",
    "sala-bano": "s777_room_restroom.png",
    "sala-caja": "s777_room_cashier_room.png",
    "sala-fumadores": "s777_room_smoking_room.png",
    "sala-parqueo": "s777_parking.png",
    "poster-trailer": "clean_intro_4_10.0.png",
}

PINS = [
    "trebol_torcido", "moneda_al_aire", "as_suelto", "ficha_extra", "reloj_de_bolsillo",
    "mazo_de_plomo", "capital_con_dientes", "vela_del_brujo", "alfiler_de_un_colon",
    "palanca_de_una_sola_fe", "barra_fria", "borde_dorado", "campana_de_servicio",
    "cinta_de_dos_pares", "frutas_de_feria", "maquina_en_ayunas", "par_que_arrastra",
    "siete_en_mitades", "ultima_tirada", "casilla_dorada", "doble_oportunidad",
    "docena_del_cobrador", "docena_del_medio", "numero_del_dia", "pano_rojo",
    "tres_en_una_casilla", "vecino_maldito", "pagare_liviano", "ventana_larga",
    "cuatro_en_la_mesa", "reroll_de_bolsillo", "segunda_lengua",
]

# Colores de la paleta maestra que usa el sitio.
WINE_0 = (36, 6, 10)       # c224
WINE_1 = (58, 22, 29)      # c118
WINE_2 = (87, 28, 39)      # c007
RED = (200, 24, 34)        # c001
RED_HI = (221, 41, 45)     # c011
GOLD = (255, 200, 37)      # c008
GOLD_DEEP = (255, 162, 20)  # c014
GOLD_HI = (255, 242, 143)  # c029
CREAM = (255, 252, 229)    # c124
INK = (19, 13, 16)         # c282


def x2(im: Image.Image, k: int = 2) -> Image.Image:
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def build_shots(captures: Path) -> None:
    out = IMG / "shots"
    out.mkdir(parents=True, exist_ok=True)
    for name, src in SHOTS.items():
        im = Image.open(captures / src).convert("RGB")
        assert im.size == (640, 360), f"{src}: {im.size}"
        x2(im).save(out / f"{name}.webp", lossless=True, quality=100, method=6)
        im.save(out / f"{name}-1x.webp", lossless=True, quality=100, method=6)


def build_map(captures: Path) -> None:
    out = IMG / "map"
    out.mkdir(parents=True, exist_ok=True)
    im = Image.open(captures / "casino_map_777.png").convert("RGBA")
    bg = Image.new("RGBA", im.size, (18, 8, 11, 255))
    bg.alpha_composite(im)
    bg.convert("RGB").save(out / "casino.webp", lossless=True, quality=100, method=6)


def build_pins(game: Path) -> None:
    out = IMG / "pins"
    out.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGBA", (16 * 8, 16 * 4), (0, 0, 0, 0))
    for i, pin in enumerate(PINS):
        icon = Image.open(game / f"assets/icons/amulets/{pin}_16.png").convert("RGBA")
        sheet.alpha_composite(icon, ((i % 8) * 16, (i // 8) * 16))
    sheet.save(out / "pins.png", optimize=True)


def build_sprites(game: Path) -> None:
    out = IMG / "ui"
    out.mkdir(parents=True, exist_ok=True)
    coin = Image.open(game / "assets/sprites/props/win_coin.png").convert("RGBA")
    coin.save(out / "coin.png", optimize=True)
    smoke = Image.open(game / "assets/sprites/animations/smoke/smoke_puffs.png").convert("RGBA")
    smoke.save(out / "smoke.png", optimize=True)


def build_carpet() -> None:
    """Baldosa de 32x16: rombos anidados, como la alfombra de casino, en vino oscuro.

    Dibujada para la web: no es la alfombra del pack (que no se redistribuye suelta).
    """
    w, h = 32, 16
    im = Image.new("RGB", (w, h), WINE_0)
    px = im.load()
    for y in range(h):
        for x in range(w):
            # distancia "manhattan" al centro de cada rombo (dos por baldosa)
            dx = min(abs(x - 8), abs(x - 24))
            dy = abs(y - 8)
            d = dx / 8 + dy / 8
            if abs(d - 1.0) < 0.07:
                px[x, y] = WINE_2
            elif abs(d - 0.55) < 0.07:
                px[x, y] = WINE_1
    # punto dorado apagado en el centro de cada rombo y en las esquinas
    for cx, cy in ((8, 8), (24, 8), (0, 0), (16, 0)):
        px[cx % w, cy % h] = (127, 46, 45)  # c068
    im.save(IMG / "ui" / "carpet.png", optimize=True)


CHIP = [
    "....wwrrrrww....",
    "..rrwwrrrrwwrr..",
    ".rrrrrrrrrrrrrr.",
    ".rrrrggggggrrrr.",
    "wwrrgggggggggrww",
    "wwrggrrrrrrggrww",
    "rrrggrrrrrrggrrr",
    "rrrggrrrrrrggrrr",
    "rrrggrrrrrrggrrr",
    "rrrggrrrrrrggrrr",
    "wwrggrrrrrrggrww",
    "wwrrgggggggggrww",
    ".rrrrggggggrrrr.",
    ".rrrrrrrrrrrrrr.",
    "..rrwwrrrrwwrr..",
    "....wwrrrrww....",
]
CHIP_COLORS = {"r": RED, "w": CREAM, "g": GOLD}


def chip_image(scale: int, pad: int = 0, bg: tuple | None = None) -> Image.Image:
    size = 16 * scale + pad * 2
    im = Image.new("RGBA", (size, size), (*bg, 255) if bg else (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y, row in enumerate(CHIP):
        for x, ch in enumerate(row):
            if ch in CHIP_COLORS:
                x0, y0 = pad + x * scale, pad + y * scale
                d.rectangle([x0, y0, x0 + scale - 1, y0 + scale - 1], fill=CHIP_COLORS[ch])
    # contorno oscuro de 1 px de arte para que se lea sobre fondos claros
    return im


def build_icons() -> None:
    out = IMG / "icons"
    out.mkdir(parents=True, exist_ok=True)
    rects = []
    for y, row in enumerate(CHIP):
        for x, ch in enumerate(row):
            if ch in CHIP_COLORS:
                r, g, b = CHIP_COLORS[ch]
                rects.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="#{r:02x}{g:02x}{b:02x}"/>')
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" '
           'shape-rendering="crispEdges">' + "".join(rects) + "</svg>\n")
    (out / "favicon.svg").write_text(svg, encoding="utf-8")
    chip_image(2).save(out / "favicon-32.png", optimize=True)
    chip_image(10, 10, WINE_0).save(out / "apple-touch-icon.png", optimize=True)  # 180
    chip_image(10, 16, WINE_0).resize((192, 192), Image.NEAREST).save(out / "icon-192.png")
    chip_image(28, 32, WINE_0).resize((512, 512), Image.NEAREST).save(out / "icon-512.png")
    ico = chip_image(3)  # 48
    ico.save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])


def geist(size: float, shape: str | None = None) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(ROOT / "tools" / ".cache" / "GeistPixel.ttf"), size)
    if shape:
        font.set_variation_by_name(shape)
    return font


def build_og(game: Path) -> None:
    import zipfile

    cache = ROOT / "tools" / ".cache"
    cache.mkdir(exist_ok=True)
    with zipfile.ZipFile(game / "assets/fonts/Geist_Pixel.zip") as zf:
        (cache / "GeistPixel.ttf").write_bytes(
            zf.read("GeistPixel-Regular-VariableFont_ELSH.ttf"))

    hero = IMG / "hero"
    comp = Image.new("RGBA", (960, 1088), (*WINE_0, 255))
    comp.alpha_composite(Image.open(hero / "hero-back.webp").convert("RGBA"))
    for layer in ("hero-bulbs-band-0", "hero-bulbs-band-1", "hero-sign", "hero-bulbs-sign-0",
                  "hero-bulbs-sign-1", "hero-front"):
        comp.alpha_composite(Image.open(hero / f"{layer}.webp").convert("RGBA"), (160, 0))
    # 600x315 de arte -> 1200x630. El arte empieza en x=160 de la composicion.
    crop = comp.crop((180, 218, 780, 533))
    base = x2(crop.convert("RGB")).convert("RGBA")

    # Franja oscura arriba para el titulo: escalones de 2 px de arte, sin degradado suave.
    shade = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(shade)
    for i, a in enumerate((235, 230, 222, 210, 190, 160, 120, 80, 45, 20)):
        d.rectangle([0, i * 16, 1200, i * 16 + 15], fill=(*INK, a))
    base.alpha_composite(shade)

    cell = 1000 / 38  # tamano en px para que una celda de la fuente sea 1 px
    for lang, tag, warn in (
        ("es", "Solo una más.", "+18 · Apuestas simuladas · Sin dinero real"),
        ("en", "Just one more.", "18+ · Simulated gambling · No real money"),
    ):
        im = base.copy()
        d = ImageDraw.Draw(im)
        title = "JUST ONE MORE BET"
        f_title = geist(cell * 3, "Circle")
        tw = d.textlength(title, font=f_title)
        x = (1200 - tw) / 2
        d.text((x + 3, 30 + 3), title, font=f_title, fill=(*RED, 255))
        d.text((x, 30), title, font=f_title, fill=(*GOLD, 255))
        f_tag = geist(cell * 1.5)
        tg = d.textlength(tag, font=f_tag)
        d.text(((1200 - tg) / 2 + 3, 121), tag, font=f_tag, fill=(*INK, 255))
        d.text(((1200 - tg) / 2, 118), tag, font=f_tag, fill=(*CREAM, 255))
        # Placa del aviso abajo a la derecha.
        f_warn = geist(cell)
        ww = d.textlength(warn, font=f_warn)
        bx0, by0 = 1200 - ww - 44, 630 - 58
        d.rectangle([bx0, by0, 1200 - 16, 630 - 16], fill=(*INK, 235), outline=(*GOLD_DEEP, 255),
                    width=2)
        d.text((bx0 + 14, by0 + 9), warn, font=f_warn, fill=(*GOLD_HI, 255))
        im.convert("RGB").save(IMG / "og" / f"og-{lang}.png", optimize=True)


def main() -> None:
    captures = Path(sys.argv[1])
    game = Path(sys.argv[2])
    for sub in ("shots", "pins", "ui", "icons", "og", "map"):
        (IMG / sub).mkdir(parents=True, exist_ok=True)
    build_shots(captures)
    build_map(captures)
    build_pins(game)
    build_sprites(game)
    build_carpet()
    build_icons()
    build_og(game)
    total = sum(f.stat().st_size for f in IMG.rglob("*") if f.is_file())
    print(f"assets/img: {total / 1024:.0f} KB")


if __name__ == "__main__":
    main()
