"""Hero nocturno de la web: el parqueo del casino deco, de noche, por capas.

Entrada: las capas que saca `tools/godot/render_parking_layers.gd` del juego (parqueo deco a
resolucion nativa, fondo transparente). Salida en `assets/img/hero/`:

  hero-back.png    suelo + fachada + leon, graduado de noche
  hero-sign.png    cartel de Las Vegas y totem, de noche, bombillas apagadas
  hero-front.png   palmeras, jardineras, farolas y bolardos (la capa mas cercana)
  hero-bulbs-0..2  bombillas encendidas por fase, para la persecucion de la marquesina
  hero-glow.png    halos de luz de las farolas y del leon (se dibuja con 'lighter')

Todo color de salida se ajusta a `tools/art/master_palette.gpl` del juego: la noche no mete
colores nuevos, solo elige otros de la misma paleta.

Uso:
  python tools/build_hero.py <carpeta_capas> <ruta_juego>
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial import cKDTree

OUT = Path(__file__).resolve().parent.parent / "assets" / "img" / "hero"

# Alto del escenario en pixeles de arte: la sala entera, del tejado al fondo del parqueo.
STAGE_H = 1088
# La capa de fondo se ensancha por espejo a cada lado, para pantallas anchas.
MARGIN = 160

# Luz ambiente de noche: azul y oscura. Lo iluminado se acerca a 1 con un tinte calido.
AMBIENT = np.array([0.20, 0.23, 0.40])
WARM = np.array([1.00, 0.90, 0.74])

BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def load_palette(game: Path) -> np.ndarray:
    cols = []
    for line in (game / "tools/art/master_palette.gpl").read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) >= 3 and all(p.isdigit() for p in parts[:3]):
            cols.append([int(p) for p in parts[:3]])
    return np.array(cols, dtype=np.float64)


class Snapper:
    """Ajusta colores a la paleta maestra, con un peso perceptual simple."""

    W = np.array([0.30, 0.59, 0.11]) ** 0.5

    def __init__(self, palette: np.ndarray):
        self.palette = palette
        self.tree = cKDTree(palette * self.W)

    def snap(self, rgb: np.ndarray) -> np.ndarray:
        flat = rgb.reshape(-1, 3)
        uniq, inv = np.unique(np.round(flat).astype(np.int32), axis=0, return_inverse=True)
        _, idx = self.tree.query(uniq * self.W)
        return self.palette[idx][inv.reshape(-1)].reshape(rgb.shape).astype(np.uint8)


def rgba(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGBA")).astype(np.float64)[:STAGE_H]


def over(dst: np.ndarray, src: np.ndarray) -> np.ndarray:
    a = src[..., 3:4] / 255.0
    out = dst.copy()
    out[..., :3] = src[..., :3] * a + dst[..., :3] * (1 - a)
    out[..., 3:4] = np.maximum(dst[..., 3:4], src[..., 3:4])
    return out


def ellipse(h: int, w: int, cx: float, cy: float, rx: float, ry: float) -> np.ndarray:
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    return np.clip(1.0 - d, 0.0, 1.0)


def stepped(light: np.ndarray, levels: list[float]) -> np.ndarray:
    """Posteriza la luz en escalones duros, con damero solo en una franja estrecha del borde.

    Es como el juego pinta la luz de las farolas: escalones con el borde en damero. Tramar
    toda la rampa llenaria la fachada de ruido; solo se trama la costura entre escalones.
    """
    h, w = light.shape
    yy, xx = np.mgrid[0:h, 0:w]
    checker = ((xx + yy) % 2).astype(bool)
    n = len(levels) - 1
    scaled = np.clip(light, 0, 1) * n
    base = np.floor(scaled)
    frac = scaled - base
    up = (frac > 0.62) | ((frac > 0.38) & checker)
    idx = np.clip(base + up, 0, n).astype(int)
    return np.array(levels)[idx]


def color_mask(img: np.ndarray, colors: list[tuple[int, int, int]]) -> np.ndarray:
    m = np.zeros(img.shape[:2], dtype=bool)
    for c in colors:
        m |= np.all(np.abs(img[..., :3] - np.array(c)) < 1, axis=-1) & (img[..., 3] > 0)
    return m


def grade(img: np.ndarray, light: np.ndarray, snapper: Snapper) -> np.ndarray:
    lit = light[..., None]
    mul = AMBIENT * (1 - lit) + WARM * lit
    rgb = img[..., :3] * mul
    out = img.copy()
    out[..., :3] = snapper.snap(rgb)
    return out


def save(arr: np.ndarray, name: str) -> None:
    a = np.clip(arr, 0, 255).astype(np.uint8)
    a[a[..., 3] == 0] = 0
    Image.fromarray(a, "RGBA").save(OUT / name, optimize=True)
    print(f"  {name}  {a.shape[1]}x{a.shape[0]}")


def main() -> None:
    layers = Path(sys.argv[1])
    game = Path(sys.argv[2])
    OUT.mkdir(parents=True, exist_ok=True)
    snapper = Snapper(load_palette(game))

    ground = rgba(layers / "parking_ground.png")
    lot = rgba(layers / "parking_lot.png")
    facade = rgba(layers / "parking_facade.png")
    sign = rgba(layers / "parking_sign.png")
    front = rgba(layers / "parking_front.png")
    h, w = ground.shape[:2]

    back = over(over(ground, lot), facade)

    # --- Mapa de luz -------------------------------------------------------------------
    light = np.zeros((h, w))
    # Focos que suben del estrado al leon: lo mas iluminado de la escena. Solo dentro del
    # portal (x 184-456): fuera, un ovalo de luz sobre las ventanas se leia como un error.
    portal = np.zeros((h, w))
    portal[286:548, 184:456] = 1.0
    light = np.maximum(light, portal * np.clip(ellipse(h, w, 320, 500, 190, 260) * 1.8, 0, 1))
    # Derrame suave sobre la piedra de alrededor.
    light = np.maximum(light, ellipse(h, w, 320, 470, 230, 200) * 0.55)
    # La banda de la marquesina de la fachada, a lo largo.
    band = np.zeros((h, w))
    band[478:506, :] = 0.75
    light = np.maximum(light, band)
    # Farolas de la plaza y del parqueo: charco de luz bajo cada una.
    for cx, cy, r in [(200, 690, 70), (440, 690, 70), (264, 790, 60), (376, 790, 60),
                      (264, 966, 60), (376, 966, 60)]:
        light = np.maximum(light, ellipse(h, w, cx, cy, r * 1.3, r) * 1.6)
    # La alfombra roja hasta el bordillo: la puerta la alumbra.
    light = np.maximum(light, ellipse(h, w, 320, 600, 40, 120) * 1.2)
    light = np.clip(light, 0, 1)
    light = stepped(light, [0.0, 0.32, 0.6, 0.86, 1.0])

    # Ventanas: los paneles naranjas se encienden (luz de dentro), los oscuros quedan azules.
    warm_panes = color_mask(back, [(196, 128, 52), (168, 100, 26)])
    # La claraboya del tejado (y 150-230) queda apagada: encendida competia con el titulo, que
    # en la web cae justo encima.
    warm_panes[150:230, :] = False
    light_back = light.copy()
    light_back[warm_panes] = 1.0
    # El interior de la boca del leon: negro calido, no azul.
    night_back = grade(back, light_back, snapper)
    # Ventanas encendidas: un punto mas de brillo para que se lean como luz y no como pintura.
    pane_rgb = np.array([255, 186, 23], dtype=np.float64)
    night_back[warm_panes, :3] = snapper.snap((back[warm_panes, :3] * 0.6 + pane_rgb * 0.4)[None])[0]

    # --- Cartel ------------------------------------------------------------------------
    sign_light = np.where(sign[..., 3] > 0, 0.9, 0.0)
    # Los postes y el totem no se alumbran solos.
    sign_light[500:, :] = np.minimum(sign_light[500:, :], 0.45)
    sign_light[:, 540:] = np.minimum(sign_light[:, 540:], 0.55)
    night_sign = grade(sign, sign_light, snapper)

    # Bombillas: los puntos amarillo claro del borde del cartel.
    bulb_cols = [(253, 204, 107), (250, 215, 149), (246, 200, 112)]
    bulbs = color_mask(sign, bulb_cols)
    # Fuera la cara del cartel: ahi el amarillo es letra, no bombilla.
    face = ndimage.binary_fill_holes(color_mask(sign, [(253, 247, 234), (253, 251, 248)]))
    face = ndimage.binary_dilation(face, iterations=1)
    bulbs &= ~face
    # Y las bolitas de la marquesina de la fachada (puntos claros en la banda granate).
    band_bulbs = np.zeros_like(bulbs)
    band_rows = slice(478, 506)
    sub = back[band_rows]
    bright = (sub[..., :3].sum(-1) > 600) & (sub[..., 3] > 0)
    band_bulbs[band_rows] = bright
    labels, n = ndimage.label(bulbs | band_bulbs)
    print(f"  bombillas: {n}")
    centers = ndimage.center_of_mass(np.ones_like(labels), labels, range(1, n + 1))

    # Las bombillas apagadas: ambar oscuro en la capa del cartel y de la fachada.
    off = np.array([132, 51, 9], dtype=np.float64)
    for arr, mask in ((night_sign, bulbs), (night_back, band_bulbs)):
        arr[mask, :3] = snapper.snap(off[None, None, :].repeat(mask.sum(), 1))[0]

    # Fases de la persecucion: orden por angulo alrededor del cartel, y de izquierda a derecha
    # en la banda de la fachada. Dos juegos de capas, porque el cartel tiene parallax propio
    # y sus bombillas tienen que viajar con el.
    on_core = np.array([255, 242, 143])
    on_ring = np.array([255, 162, 20])
    groups = {"sign": [], "band": []}
    for i, (cy, cx) in enumerate(centers, start=1):
        if bulbs[int(round(cy)), int(round(cx))] or (labels == i)[bulbs].any():
            groups["sign"].append((np.arctan2(cy - 410, cx - 117), i))
        else:
            groups["band"].append((cx, i))
    phases = {g: [np.zeros((h, w, 4)) for _ in range(3)] for g in groups}
    for g, items in groups.items():
        items.sort()
        for rank, (_, label) in enumerate(items):
            mask = labels == label
            ring = ndimage.binary_dilation(mask, iterations=1) & ~mask
            p = phases[g][rank % 3]
            p[ring, :3] = on_ring
            p[ring, 3] = 150
            p[mask, :3] = on_core
            p[mask, 3] = 255
    print(f"  bombillas del cartel: {len(groups['sign'])}, de la fachada: {len(groups['band'])}")

    # --- Primer plano ------------------------------------------------------------------
    front_light = np.zeros((h, w))
    for cx, cy, r in [(200, 650, 80), (440, 650, 80)]:
        front_light = np.maximum(front_light, ellipse(h, w, cx, cy, r, r) * 1.4)
    front_light = stepped(np.clip(front_light, 0, 1), [0.0, 0.3, 0.6, 0.9])
    night_front = grade(front, front_light, snapper)
    # Las cabezas de las farolas: encendidas.
    lamp_heads = color_mask(front, [(255, 242, 143), (255, 235, 87), (253, 204, 107),
                                    (255, 255, 255), (250, 215, 149)])
    night_front[lamp_heads, :3] = [255, 242, 143]

    # Espejo a los lados: la fachada se repite en bahias simetricas, asi que reflejada sigue.
    wide = np.concatenate(
        [night_back[:, MARGIN - 1::-1], night_back, night_back[:, :-MARGIN - 1:-1]], axis=1
    )
    save(wide, "hero-back.png")
    save(night_sign, "hero-sign.png")
    save(night_front, "hero-front.png")
    for g in phases:
        for i, p in enumerate(phases[g]):
            save(p, f"hero-bulbs-{g}-{i}.png")

    # Vista previa compuesta (no se publica).
    comp = over(over(night_back, night_sign), night_front)
    comp_wide = wide.copy()
    comp_wide[:, MARGIN:MARGIN + w] = comp
    for g in phases:
        for p in phases[g][:2]:
            comp = over(comp, p)
    preview = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    if preview:
        Image.fromarray(comp_wide.astype(np.uint8), "RGBA").save(preview)


if __name__ == "__main__":
    main()
