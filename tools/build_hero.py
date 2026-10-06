"""Hero nocturno de la web: el parqueo del casino deco, de noche, por capas.

Entrada: las capas que saca `tools/godot/render_parking_layers.gd` del juego (parqueo deco a
resolucion nativa, fondo transparente). Salida en `assets/img/hero/`:

  hero-back.webp          suelo + fachada + leon, graduado de noche, 960 de ancho (espejo)
  hero-sign.webp          cartel de Las Vegas y totem, de noche, bombillas apagadas
  hero-front.webp         palmeras, jardineras, farolas y bolardos (la capa mas cercana)
  hero-bulbs-sign-0..2    bombillas del cartel encendidas, una capa por fase de la persecucion
  hero-bulbs-band-0..2    lo mismo para la marquesina de la fachada

Todo color de salida se ajusta a `tools/art/master_palette.gpl` del juego: la noche no mete
colores nuevos, solo elige otros de la misma paleta.

La fachada pintada a mano por Samuel trae el cartel de Las Vegas dentro del mismo PNG (ya no es
un sprite suelto). Si la capa del cartel llega vacia, se busca el cartel del juego
(`parking_vegas_sign_deco.png`) pegado en la fachada, se pasa a su capa para que siga teniendo
parallax, y el hueco que deja se rellena: fuera del portal con la fachada deco, que es el mismo
edificio; dentro, con el reflejo del portal, que es simetrico.

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

# El cartel de Las Vegas y la fachada deco sin cartel pintado, en el repo del juego.
SIGN_SPRITE = "assets/sprites/props/parking_vegas_sign_deco.png"
FACADE_DECO = "assets/sprites/props/casino_entrance_facade_deco.png"
# Esquina del cartel cuando era un sprite suelto de la escena deco. Las coordenadas de luz del
# cartel (postes, centro de la persecucion) se midieron ahi y se corren con el cartel.
SIGN_REF = (0, 262)
# Columnas del portal de la fachada: dentro esta el leon, fuera las bahias de ventanas.
PORTAL_X = (184, 456)


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


def find_sprite(layer: np.ndarray, sprite: np.ndarray) -> tuple[int, int] | None:
    """Esquina donde `sprite` esta pegado tal cual (pixeles opacos identicos) en `layer`."""
    opaque = sprite[..., 3] > 0
    ys, xs = np.nonzero(opaque)
    h, w = sprite.shape[:2]
    rows, cols = layer.shape[0] - h + 1, layer.shape[1] - w + 1
    if rows <= 0 or cols <= 0:
        return None
    # Criba con una muestra de pixeles; luego se comprueba el sprite entero.
    hits = np.ones((rows, cols), dtype=bool)
    for i in np.linspace(0, len(ys) - 1, 96).astype(int):
        ty, tx = ys[i], xs[i]
        hits &= np.all(layer[ty:ty + rows, tx:tx + cols] == sprite[ty, tx], axis=-1)
        if not hits.any():
            return None
    for y, x in zip(*np.nonzero(hits)):
        if np.all(layer[y:y + h, x:x + w][opaque] == sprite[opaque]):
            return int(x), int(y)
    return None


def split_painted_sign(facade: np.ndarray, game: Path) -> tuple[np.ndarray, np.ndarray, tuple]:
    """Saca el cartel pintado en la fachada a su propia capa y rellena el hueco.

    Devuelve (fachada sin cartel, cartel, desplazamiento del cartel respecto de `SIGN_REF`).
    """
    sprite = np.asarray(Image.open(game / SIGN_SPRITE).convert("RGBA")).astype(np.float64)
    at = find_sprite(facade, sprite)
    if at is None:
        sys.exit("build_hero: la capa del cartel esta vacia y el cartel no aparece en la fachada")
    x0, y0 = at
    h, w = sprite.shape[:2]
    mask = np.zeros(facade.shape[:2], dtype=bool)
    mask[y0:y0 + h, x0:x0 + w] = sprite[..., 3] > 0
    sign = np.zeros_like(facade)
    sign[mask] = facade[mask]

    deco = np.zeros_like(facade)
    d = np.asarray(Image.open(game / FACADE_DECO).convert("RGBA")).astype(np.float64)
    d = d[:facade.shape[0], :facade.shape[1]]
    deco[:d.shape[0], :d.shape[1]] = d
    # Fuera del portal la deco tiene que ser la misma fachada; si no, el relleno inventaria.
    wing = ~mask & (facade[..., 3] > 0) & (deco[..., 3] > 0)
    wing[:, PORTAL_X[0]:PORTAL_X[1]] = False
    same = np.all(facade[wing] == deco[wing], axis=-1).mean()
    if same < 0.95:
        sys.exit(f"build_hero: la fachada deco ya no coincide con la del juego ({same:.0%})")
    fill = np.where((np.arange(facade.shape[1]) < PORTAL_X[0])[None, :, None],
                    deco, facade[:, ::-1])
    back = facade.copy()
    back[mask] = fill[mask]
    print(f"  cartel pintado en ({x0}, {y0}): {mask.sum()} px a su capa")
    return back, sign, (x0 - SIGN_REF[0], y0 - SIGN_REF[1])


def save(arr: np.ndarray, name: str) -> None:
    a = np.clip(arr, 0, 255).astype(np.uint8)
    a[a[..., 3] == 0] = 0
    # WebP sin perdida: la mitad que el PNG (la capa de fondo, de 122 a 47 KB).
    Image.fromarray(a, "RGBA").save(OUT / name, lossless=True, quality=100, method=6, exact=True)
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
    sx, sy = 0, 0
    if sign[..., 3].max() == 0:
        facade, sign, (sx, sy) = split_painted_sign(facade, game)

    back = over(over(ground, lot), facade)

    # --- Mapa de luz -------------------------------------------------------------------
    light = np.zeros((h, w))
    # Focos que suben del estrado al leon: lo mas iluminado de la escena. Solo dentro del
    # portal (x 184-456): fuera, un ovalo de luz sobre las ventanas se leia como un error.
    portal = np.zeros((h, w))
    portal[286:548, 184:456] = 1.0
    # El leon de pie baja las patas a la plaza, por debajo del estrado: los mismos focos las
    # alumbran, solo a ellas (pixeles de la fachada), no a las baldosas de alrededor.
    paws = np.zeros((h, w), dtype=bool)
    paws[548:600, PORTAL_X[0]:PORTAL_X[1]] = facade[548:600, PORTAL_X[0]:PORTAL_X[1], 3] > 0
    portal[paws] = 1.0
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
    # En el portal no hay ventanas: esos naranjas son del leon, que ya alumbran los focos.
    warm_panes[286:600, PORTAL_X[0]:PORTAL_X[1]] = False
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
    sign_light[500 + sy:, :] = np.minimum(sign_light[500 + sy:, :], 0.45)
    sign_light[:, 540 + sx:] = np.minimum(sign_light[:, 540 + sx:], 0.55)
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
    # La marquesina se corta en el portal: lo claro de ahi es el leon, no bombillas.
    band_bulbs[:, PORTAL_X[0]:PORTAL_X[1]] = False

    # Las bombillas apagadas: ambar oscuro en la capa del cartel y de la fachada.
    off = np.array([132, 51, 9], dtype=np.float64)
    for arr, mask in ((night_sign, bulbs), (night_back, band_bulbs)):
        arr[mask, :3] = snapper.snap(off[None, None, :].repeat(mask.sum(), 1))[0]

    # Fases de la persecucion: orden por angulo alrededor del cartel, y de izquierda a derecha
    # en la banda de la fachada. Dos juegos de capas, porque el cartel tiene parallax propio
    # y sus bombillas tienen que viajar con el.
    on_core = np.array([255, 242, 143])
    on_ring = np.array([255, 162, 20])
    # Cada grupo se etiqueta por separado: el cartel tapa un tramo de la marquesina y sus
    # bombillas no se pueden fundir con las de la fachada que quedan detras.
    groups = {"sign": [], "band": []}
    labeled = {}
    for g, found in (("sign", bulbs), ("band", band_bulbs)):
        labeled[g], n = ndimage.label(found)
        for i, (cy, cx) in enumerate(
                ndimage.center_of_mass(found, labeled[g], range(1, n + 1)), start=1):
            key = np.arctan2(cy - (410 + sy), cx - (117 + sx)) if g == "sign" else cx
            groups[g].append((key, i))
    phases = {g: [np.zeros((h, w, 4)) for _ in range(3)] for g in groups}
    for g, items in groups.items():
        items.sort()
        for rank, (_, label) in enumerate(items):
            mask = labeled[g] == label
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
    save(wide, "hero-back.webp")
    save(night_sign, "hero-sign.webp")
    save(night_front, "hero-front.webp")
    for g in phases:
        for i, p in enumerate(phases[g]):
            save(p, f"hero-bulbs-{g}-{i}.webp")

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
