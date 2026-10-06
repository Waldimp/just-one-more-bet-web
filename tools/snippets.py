"""Bloques repetitivos de la portada: los 32 pines y la escalera de 15 plazos.

Rellena los marcadores <!--PINS--> y <!--LADDER--> de index.html y en/index.html (si siguen
ahi). Uso: python tools/snippets.py
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# indice en pins.png, nombre ES, nombre EN, rareza
PINS = [
    ("Trébol torcido", "Crooked Clover", "common"),
    ("Moneda al aire", "Coin Toss", "common"),
    ("As suelto", "Loose Ace", "common"),
    ("Ficha extra", "Extra Chip", "unusual"),
    ("Reloj de bolsillo", "Pocket Watch", "unusual"),
    ("Mazo de plomo", "Lead Deck", "rare"),
    ("Capital con dientes", "Capital with Teeth", "rare"),
    ("Vela del Brujo", "The Brujo's Candle", "rare"),
    ("Alfiler de un colón", "One-Colón Pin", "forbidden"),
    ("Palanca de una sola fe", "Lever of a Single Faith", "forbidden"),
    ("Barra fría", "Cold Bar", "common"),
    ("Borde dorado", "Golden Edge", "unusual"),
    ("Campana de servicio", "Service Bell", "unusual"),
    ("Cinta de dos pares", "Two-Pair Ribbon", "unusual"),
    ("Frutas de feria", "Fairground Fruit", "common"),
    ("Máquina en ayunas", "Fasting Machine", "forbidden"),
    ("Par que arrastra", "Dragging Pair", "unusual"),
    ("Siete en mitades", "Seven in Halves", "rare"),
    ("Última tirada", "Last Spin", "common"),
    ("Casilla dorada", "Golden Pocket", "rare"),
    ("Doble oportunidad", "Double Chance", "rare"),
    ("Docena del cobrador", "The Collector's Dozen", "unusual"),
    ("Docena del medio", "Middle Dozen", "unusual"),
    ("Número del día", "Number of the Day", "unusual"),
    ("Paño rojo", "Red Felt", "unusual"),
    ("Tres en una casilla", "Three on One Square", "rare"),
    ("Vecino maldito", "Cursed Neighbor", "rare"),
    ("Pagaré liviano", "Light IOU", "unusual"),
    ("Ventana larga", "Long Window", "rare"),
    ("Cuatro en la mesa", "Four on the Table", "unusual"),
    ("Reroll de bolsillo", "Pocket Reroll", "unusual"),
    ("Segunda lengua", "Second Tongue", "unusual"),
]
RARITY = {
    "es": {"common": "Común", "unusual": "Inusual", "rare": "Raro", "forbidden": "Prohibido"},
    "en": {"common": "Common", "unusual": "Unusual", "rare": "Rare", "forbidden": "Forbidden"},
}
LADDER = [1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 100_000, 200_000, 500_000, 1_000_000,
          2_000_000, 5_000_000, 10_000_000, 20_000_000, 50_000_000]


def pins(lang: str) -> str:
    out = []
    for i, (es, en, r) in enumerate(PINS):
        name = es if lang == "es" else en
        rar = RARITY[lang][r]
        out.append(
            f'<li><button class="pin" type="button" data-r="{r}" data-name="{name}" '
            f'data-rarity="{rar}" style="--x:{i % 8};--y:{i // 8}" '
            f'aria-label="{name} ({rar.lower()})"><i></i></button></li>'
        )
    return "\n\t\t\t\t\t\t\t\t".join(out)


def ladder() -> str:
    lo, hi = math.log10(LADDER[0]) - 0.35, math.log10(LADDER[-1])
    out = []
    for i, v in enumerate(LADDER):
        h = (math.log10(v) - lo) / (hi - lo) * 100
        out.append(f'<li style="--h:{h:.1f};--i:{i}"></li>')
    return "".join(out)


for path, lang in ((ROOT / "index.html", "es"), (ROOT / "en" / "index.html", "en")):
    if not path.exists():
        continue
    html = path.read_text(encoding="utf-8")
    html = html.replace("<!--PINS-->", pins(lang)).replace("<!--LADDER-->", ladder())
    path.write_text(html, encoding="utf-8")
    print("ok", path.relative_to(ROOT))
