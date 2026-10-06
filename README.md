# Just One More Bet — web oficial

Página oficial de **Just One More Bet**, un roguelite de casino en pixel art hecho en Godot:
saliste de la cárcel debiendo más, y la única salida es un casino con 150 segundos y 3 apuestas
por día. Apuestas simuladas, sin dinero real, +18.

Sitio **estático**: HTML, CSS y un JavaScript propio, sin dependencias ni paso de build. Sin
cookies, analíticas, trackers ni fuentes remotas, así que no necesita banner de cookies.

## Estructura

```
/                       portada en español        index.html
/en                     portada en inglés         en/index.html
/privacidad             política de privacidad    privacidad/index.html
/en/privacy             privacy policy            en/privacy/index.html
/creditos               créditos y licencias      creditos/index.html
/en/credits             credits and licenses      en/credits/index.html
/404                    página no encontrada      404.html

assets/css/site.css     todos los estilos
assets/js/boot.js       marca que hay JS antes de pintar (evita parpadeos)
assets/js/site.js       hero en canvas, revelados, HUD del día, plano, visor, tráiler, monedas
assets/fonts/           Geist Pixel recortada (5 KB + 15 KB la de bombillas), el glifo ₡ y la OFL
assets/img/hero/        el parqueo de noche por capas (fondo, cartel, primer plano, bombillas)
assets/img/shots/       capturas reales del juego, x2 vecino más cercano, WebP sin pérdida
assets/img/map/         el plano entero del casino de la semilla 777
assets/img/pins/        los 32 pines del juego (arte propio, 16x16)
assets/img/og/          imágenes para redes, 1200x630, ES y EN
assets/img/logo/        el logo del juego (64x64) y su tira de giro de 8 cuadros
assets/img/icons/       favicon e iconos de app, hechos del logo (PNG e ICO)
assets/js/menu.js       cierra el menu de la cabecera (popover nativo) al elegir un enlace
content/                el texto de la política de privacidad en Markdown (ES y EN)
media/                  los tráilers: trailer_es.mp4 y trailer_en.mp4 (35 MB cada uno)
tools/                  scripts que generan los assets (no se despliegan: .vercelignore)
vercel.json             cleanUrls, cabeceras de seguridad y caché
```

Peso total: **~1,5 MB** sin los tráilers y ~71 MB con ellos (solo se descargan si se reproducen). La portada carga primero el hero (~60 KB) y las fuentes (~20 KB);
las capturas se cargan en diferido al acercarse.

## Ver en local

```bash
npx serve .            # http://localhost:3000, con URLs limpias como en Vercel
# o, sin Node:
python -m http.server  # /privacidad/ y /en/ funcionan con la barra final
```

## Marcadores pendientes

La página de itch.io ya está puesta (2026-10-06): https://mohhamedsamu.itch.io/just-one-more-bet

| Marcador | Dónde | Qué poner |
|---|---|---|
| `https://just-one-more-bet-web.vercel.app` | `canonical`, `hreflang`, Open Graph, `sitemap.xml`, `robots.txt` | el dominio final, si cambia. Buscar y reemplazar |

Para comprobar que no queda ningún enlace interno roto (y listar los marcadores):

```bash
python tools/check_links.py
```

### Tráiler

`media/trailer_es.mp4` y `media/trailer_en.mp4`: H.264 High 1920x1080 a 60 fps, AAC 48 kHz,
86,25 s, ~35 MB cada uno, con `moov` al principio (empiezan a reproducirse sin bajar el archivo
entero). Vienen de `game-video/out/`. Están en git porque quedan por debajo del aviso de 50 MB
por archivo de GitHub; si una versión futura pasa de ~50 MB, mejor alojarla fuera (por ejemplo,
un *release* de GitHub), cambiar el `src` del `<source>` y añadir ese dominio a `media-src` en la
CSP de `vercel.json`.

El `<video>` lleva `controls`, `preload="none"` y ningún `autoplay`: no se descarga nada hasta que
alguien pulsa reproducir. Si el archivo no carga, el botón dice «Tráiler no disponible».

El póster (`assets/img/shots/poster-trailer.webp` y `-1x.webp`) es el fotograma del segundo 16
del propio tráiler, el parqueo con el león, igual en ES y en EN. Se devuelve a su pixel art
nativo de 640x360 y se guarda x2 en WebP sin pérdida:

```bash
python tools/build_poster.py ../game-video/out/trailer_es.mp4 16
```

### Política de privacidad

El texto vive en `content/privacidad.es.md` y `content/privacy.en.md` (versión 1.0, vigente
desde 2026-10-05). Para cambiarlo, edita el `.md` y regenera:

```bash
python tools/build_privacy.py
```

El script convierte el Markdown a HTML (títulos con ancla, índice, listas, tablas que en móvil
se apilan) y lo escribe entre los marcadores `<!-- PRIVACIDAD:INICIO -->` / `<!-- PRIVACIDAD:FIN -->`
(y `PRIVACY:START` / `PRIVACY:END`), más la línea de versión entre `PRIVACIDAD:VERSION`. Lo de
fuera de los marcadores —el aviso de cómo apagar el envío, la cabecera, el pie— no se toca.
Si prefieres, se puede editar a mano el HTML entre los marcadores.

**Si cambia el dominio**, hay que actualizar también `privacy_url_es` y `privacy_url_en` en
`resources/config/telemetry_online.tres` del juego: son los enlaces que el juego abre desde
Configuración. Hoy apuntan a `https://just-one-more-bet-web.vercel.app/privacidad` y
`https://just-one-more-bet-web.vercel.app/en/privacy`.

## Desplegar en Vercel

1. Entra en [vercel.com/new](https://vercel.com/new) con tu cuenta y elige **Import Git Repository**.
2. Autoriza GitHub si te lo pide y selecciona `Waldimp/just-one-more-bet-web`.
3. En la configuración del proyecto:
   - **Framework Preset:** `Other`.
   - **Root Directory:** `./` (la raíz).
   - **Build Command:** déjalo vacío (o activa *Override* y déjalo en blanco).
   - **Output Directory:** `.` (o vacío).
   - **Install Command:** vacío. No hay dependencias.
4. Pulsa **Deploy**. Vercel lee `vercel.json` solo: URLs limpias (`/privacidad` sirve
   `privacidad/index.html`), sin barra final, cabeceras de seguridad y caché de fuentes e imágenes.
5. Nombre del proyecto: `just-one-more-bet-web`, para que la URL sea
   `https://just-one-more-bet-web.vercel.app`, la que ya enlaza el juego. Si sale otra, o usas un
   dominio propio (*Settings → Domains*), reemplaza la URL en los `.html`, `sitemap.xml`,
   `robots.txt` y en `privacy_url_es` / `privacy_url_en` del juego.
6. Cada `git push` a `main` vuelve a desplegar; las otras ramas generan *previews*.

Comprobaciones después del primer despliegue: abrir `/`, `/en`, `/privacidad`, `/en/privacy`,
`/creditos` y una ruta inventada (debe salir la página 404), y pegar la URL en un validador de
Open Graph para ver la imagen de redes.

## Cómo se hicieron los assets

Nada de esto hace falta para desplegar: los resultados ya están en `assets/`. Sirve para
regenerarlos. Todo se lee del repo del juego, que no se modifica. Godot se corre siempre con el
`tools/godot.sh` del juego (fija la versión 4.7.x), y con ventana: sin rasterizador no hay imagen.
Bajo `--script` el juego guarda en `user://test_runs/` y la telemetría no toca la red.

```bash
GAME=../just-one-more-bet
OUT=/ruta/a/capturas

# 1. Capturas a 640x360 nativos: salas, mesas en juego, Brujo, barra, cobrador, intro sin texto
$GAME/tools/godot.sh --path $GAME --script $PWD/tools/godot/capture_web.gd -- $OUT 777
$GAME/tools/godot.sh --path $GAME --script $PWD/tools/godot/capture_action.gd -- $OUT 777 slots,blackjack,roulette
$GAME/tools/godot.sh --path $GAME --script $PWD/tools/godot/capture_action.gd -- $OUT 777 horses
# 2. El plano entero del casino de la semilla 777
$GAME/tools/godot.sh --path $GAME --script $PWD/tools/godot/render_casino_map.gd -- $OUT 777
# 3. El parqueo deco por capas, con fondo transparente
$GAME/tools/godot.sh --path $GAME --script $PWD/tools/godot/render_parking_layers.gd -- $OUT

python tools/build_hero.py $OUT $GAME      # versión nocturna del parqueo, con la paleta maestra
python tools/build_assets.py $OUT $GAME    # capturas x2 WebP, plano, pines, iconos, OG
python tools/build_logo.py $GAME           # logo, giro, favicon e iconos de app desde assets/icons/branding
python tools/build_fonts.py $GAME          # Geist Pixel (estatica, pixeles fundidos) + bombillas + glifo ₡
python tools/snippets.py                   # (solo si se rehacen las portadas desde cero)
```

`tools/` necesita Python 3.12 con Pillow, NumPy, SciPy, fontTools (con brotli) y skia-pathops.

## Licencias del arte en la web

- **Capturas** (`assets/img/shots`, `assets/img/map`): imágenes reales del juego. Incluyen arte de
  los packs de Jephed (Game Between The Lines) y de las cartas de Androx, que se acreditan en
  `/creditos`. La web no publica sprites sueltos de esos packs.
- **Hero y OG** (`assets/img/hero`, `assets/img/og`): la fachada deco, el león, el cartel de Las
  Vegas, las palmeras, farolas y el suelo del parqueo son arte propio del equipo (el león y el
  cartel derivan de arte generado con PixelLab y repintado a mano, ver `docs/CREDITS.md` del
  juego). La noche se pintó por script con los colores de `tools/art/master_palette.gpl`.
- **Pines, moneda y humo**: arte propio del juego.
- **Logo y favicon**: el logo del juego (`assets/icons/branding/logo_final.png` y su animación),
  arte de Walter y Samuel.
- **Alfombra de fondo**: dibujada para la web con la paleta maestra.
- **Geist Pixel**: SIL Open Font License 1.1 (`assets/fonts/OFL.txt`). El glifo ₡ (fuente
  `JOMB Colon`) es un derivado bajo la misma licencia.

## Comprobaciones

```bash
python tools/check_links.py                       # enlaces y anclas internas
npx html-validate index.html en/index.html ...    # HTML válido
```

Accesibilidad: contraste AA, foco visible, todo navegable con teclado (el plano también: flechas,
`+` y `-`), `alt` en las capturas, video con controles y sin autoplay, y `prefers-reduced-motion`
respetado (sin paneo ni zoom en el hero, bombillas fijas, sin lluvia de monedas).

## Autores

Walter Daniel Mejía Palacios (waltermejia61@hotmail.com) y Samuel Fernando Calderón Reyes
(sfernandocalderon@gmail.com).
